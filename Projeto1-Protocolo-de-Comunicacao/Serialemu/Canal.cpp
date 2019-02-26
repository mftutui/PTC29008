/*
 * To change this license header, choose License Headers in Project Properties.
 * To change this template file, choose Tools | Templates
 * and open the template in the editor.
 */

/* 
 * File:   Canal.cpp
 * Author: msobral
 * 
 * Created on 25 de Agosto de 2017, 12:50
 */

#include "Canal.h"
#include <iostream>

using namespace std;

Canal::Canal() {
  pthread_mutex_init(&mutex, NULL);
  pthread_cond_init(&cond, NULL);    
}

Canal::Canal(Options& ops, int fd1, int fd2): fd(fd1), dest_fd(fd2) {
   ber = ops.ber;
   atraso = ops.atraso;
   bitrate = ops.bitrate;
   chunk = ops.chunk;
   
   pthread_mutex_init(&mutex, NULL);
   pthread_cond_init(&cond, NULL);    
   
  // Cria tarefa de envio periodico, que envia um chunk a cada PERIODO_TX
  if (pthread_create(&tid, NULL, Canal::do_tx, (void*)this)) {
    throw ThreadException();
  }   
}

Canal::Canal(const Canal& orig) {
  pthread_mutex_init(&mutex, NULL);
  pthread_cond_init(&cond, NULL);
}

Canal::~Canal() {
      pthread_kill(tid, SIGKILL);
}

// gera um byte com uma mascara de erro aleatoria
char Canal::byte_error() const{
  int n = 0;
  char r = 0;
  int bit;
  static bool seeded = false;

  if (ber == 0) return  0;

  if (not seeded) {
    srand48(time(NULL));
    seeded = true;
  }

  for (n=0, bit=1; n < 8; n++, bit = bit<<1) {
    if (drand48() <= ber) {
      r += bit;
    }
  }
  return  r;
}

// Verifica se ha um chunk na fila que possa ser enviado.
// confere se o atraso de propagacao foi cumprido.
int Canal::verifica_fila() {
  timeval tv;
  int n = 0;
  
  pthread_mutex_lock(&mutex);

  if (txout.size() == 0) {
    pthread_mutex_unlock(&mutex);
    return 0;
  }
  gettimeofday(&tv, NULL);
#ifdef LOG
  fprintf(logf, "fila: primeiro=%p, ", f->primeiro);
  fprintf(logf, "bytes=%d, delta=%lg\n", f->primeiro->bytes, tv.tv_sec + tv.tv_usec*1e-6 - f->primeiro->time);
  fflush(logf);
#endif

  Data & opt = txout.front();
  if (tv.tv_sec + tv.tv_usec*1e-6 >= atraso) {
    int bytes;
    char * ptr;
    int limite = opt.bytes;

    ptr = opt.buffer;
    while (limite > 0) {
      bytes = write(dest_fd,  ptr, limite);
      if (bytes < 0) break; // erro ???
      limite -= bytes;
      ptr += bytes;
    }
    if (bytes > 0) n += opt.bytes;
    txout.pop_front();
  }

  pthread_mutex_unlock(&mutex);

  return  n;
}

// Adiciona um chunk na fila, aplicando os erros de bit aleatorios
int Canal::adiciona_buffer() {
  int bytes=0, n, aChunk = chunk;
  int limite = MAXIMO;
  char buffer[MAXIMO];

  // Le bytes da linha serial
  if ((bytes = read(fd, buffer, limite)) <= 0) {
      //perror("");
    return 0;
  }

  // Aplica erros de transmissao aleatorios
  if (ber > 0) {
    for (n=0; n < bytes; n++) {
      buffer[n] = buffer[n] ^ byte_error();
    }
  }

  // Guarda os bytes recebidos em pedacos de ateh "opcoes->chunk" bytes
  pthread_mutex_lock(&mutex);
  for (n=0; n < bytes; n += chunk) {
    if (n + aChunk > bytes) aChunk = bytes - n;
    Data r(aChunk, buffer+n);
    txout.push_back(r);
  }
  //printf("sinalizando: bytes lidos=%d ...\n", bytes);
  pthread_cond_signal(&cond);
  pthread_mutex_unlock(&mutex);

  return bytes;
}

/******************************************************************
 Tarefa para envio pela serial: executada por uma thread que envia
periodicamente um chunk para um dos pseudo-terminais mestres.
*****************************************************************/
void* Canal::do_tx(void * ptr) {
  Canal * chan = (Canal*)ptr;
  chan->run();
  pthread_exit(NULL);
}

void Canal::run() {
  timeval t1, t2;
  timespec tr, tm;
  int dt, win;
  //double dtx = 0;
  int n1 = 0;

  while (true) {
    pthread_mutex_lock(&mutex);
    //cout << "empty: " << txout.empty() << endl;
    if (txout.empty()) {
      //printf("esperando ...\n");
      pthread_cond_wait(&cond, &mutex);
    }
    pthread_mutex_unlock(&mutex);
    gettimeofday(&t1, NULL);
    //dtx = (t1.tv_sec - t2.tv_sec) + (t1.tv_usec - t2.tv_usec)*1e-6;
    //fprintf(stderr,"intervalo: %lf, %lf, %lf\n", dtx, n1/dtx, n2/dtx);
    n1 = verifica_fila();
    gettimeofday(&t2, NULL);
    // forçar bitrate: se transmitiu n bytes, isso deve demorar win segundos,
    // de acordo com bitrate
    dt = (t2.tv_sec - t1.tv_sec)*1000000 + (t2.tv_usec - t1.tv_usec);
    win = n1*8*1000000;
    win = win/bitrate;
    win = win - dt;
#ifdef LOG
    fprintf(logf, "verifica_fila: %d bytes, e vai dormir %d microssegundos\n", n1+n2, win);
    fflush(logf);
#endif
    if (win > 0) {
        tr.tv_sec = 0;
        tr.tv_nsec = win*1000;
        nanosleep(&tr, &tm);
    }
  }
  pthread_exit(NULL);
}