/*
 * To change this license header, choose License Headers in Project Properties.
 * To change this template file, choose Tools | Templates
 * and open the template in the editor.
 */

/* 
 * File:   main.cpp
 * Author: msobral
 *
 * Created on 24 de Agosto de 2017, 09:13
 */

#include <iostream>

#include <sys/select.h>
//#include <sys/time.h>

#include "Argparse.h"
#include "tipos.h"
#include "Canal.h"
#include "Pts.h"

using namespace std;

/*
 * 
 */
void ajuda(char * path) {
  printf("Uso: %s [-b BER][-a atraso][-f][-B taxa_bits] | -h\n", path);
  printf("\nBER: taxa de erro de bit, que deve estar no intervalo  [0,1]\n");
  printf("atraso: atraso de propagação, em milissegundos.\n");
  printf("taxa_bits: taxa de bits em bits/segundo\n");
  printf("-f: executa em primeiro plano (nao faz fork)\n\n");
}

int parse_args(char **argv, Options & opcoes) {
    Argparse args;
    int  atraso;
    char op;
    
    args.add_option('b', "0");
    args.add_option('B', "9600");
    args.add_option('a', "0");
    args.add_flag('h');
    args.add_flag('f');
    
    try {
        args.parse(argv);
    } catch (InvalidOption e) {
        cout << "Erro: opção " << e.what() << " desconhecida" << endl;
        return 0;
    }

    if (args.get_flag('h')) {
        ajuda(argv[0]);
        return 0;
    }
    
    try {
        opcoes.ber = stoi(args['b']);
        if ((opcoes.ber < 0) || (opcoes.ber > 1)) {
            printf("Erro: BER (taxa de erro de bit) deve estar no intervalo [0,1]\n");
            return 0;
        }
    } catch (...) {
        printf("Erro: opção -b requer um valor real para BER (taxa de erro de bit)\n");
        return 0;
    }
    
    try {
        opcoes.atraso = stoi(args['a']);
        if (atraso < 0) {
          printf("Erro: atraso deve ser > 0\n");
          return 0;
        }
    } catch (...) {
        printf("Erro: opção -a requer um valor inteiro (atraso em milissegundos)\n");
        return 0;
    }
    
    try {
        opcoes.bitrate = stoi(args['B']);
        if (opcoes.bitrate <= 0) {
          printf("Erro: taxa de bits deve ser > 0\n");
          return 0;
        }
    } catch (...) {
        printf("Erro: opção -B requer um valor inteiro para taxa de bits (em bits/segundo)\n");
        return 0;
    }
    
    opcoes.bg = not args.get_flag('f');

    opcoes.chunk = MAXIMO;

    return  1;
}

int main(int argc, char** argv) {
  Options opcoes;
  int fd1, fd2;
  
  if (! parse_args(argv, opcoes)) return  0;

  //printf("rate=%d, chunk=%d\n", opcoes.bitrate, opcoes.chunk);
  //return 0;

  try {
    Pts serial1, serial2;
  
    // cria os dois pseudo-terminais, mostrando seus pathnames na tela
    cout << serial1.get_slave() << " " <<  serial2.get_slave() << endl;

    // fecha os escravos (aqui nao serao necessarios)
    //serial1.close_slave();
    //serial2.close_slave();

    // se for para rodar como daemon, vai pra 2o plano ...
    if (opcoes.bg) {
        if (fork()) {
            return 0;
        }
    }

    #ifdef LOG
    logf = fopen("se.log", "w");
    #endif

    fd1 = serial1.get_fd();
    fd2 = serial2.get_fd();
  } catch (PtsException e) {
      cout << "Erro ao criar pseudo-terminais: " << e.what() << endl;
      return errno;
  }

  int maxfd = fd1;
  if (maxfd < fd2) maxfd = fd2;
  
  try {
      Canal c1(opcoes, fd1, fd2);
      Canal c2(opcoes, fd2, fd1);

      // laco principal: espera chegar algo por ao menos um dos pseudo-terminais, e entao
      // adiciona os chunks recebidos na fila de saida do outro pseudo-terminal
      fd_set rfds, wfds;
      int n;  
      //timeval timeout;  
      while (true) {
        FD_ZERO(&rfds);
        FD_ZERO(&wfds);
        FD_SET(fd1, &rfds);
        FD_SET(fd2, &rfds);
        n = select(maxfd+1, &rfds, NULL, NULL,  NULL);
        int bytes = 0;

        if (n > 0) {
          if (FD_ISSET(fd1, &rfds)) {
            bytes += c1.adiciona_buffer();
    #ifdef LOG
            fprintf(logf, "0 -> 1: %d\n", bytes);
            fflush(logf);
    #endif
          }
          if (FD_ISSET(fd2, &rfds)) {
            bytes += c2.adiciona_buffer();
    #ifdef LOG
            fprintf(logf, "1 -> 0: %d\n", bytes);
            fflush(logf);
    #endif
          }
          if (bytes == 0) {
              sleep(1);
          }
        } else {
          perror("");
          break;
        }
      }
  } catch (ThreadException e) {
      cout << "Erro: não conseguiu criar threads para a serial: " << e.what() << endl;
  } 
}

