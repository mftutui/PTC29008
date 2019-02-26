/*
 * To change this license header, choose License Headers in Project Properties.
 * To change this template file, choose Tools | Templates
 * and open the template in the editor.
 */

/* 
 * File:   Canal.h
 * Author: msobral
 *
 * Created on 25 de Agosto de 2017, 12:50
 */

#ifndef CANAL_H
#define CANAL_H

#include <cstdlib>
#include <cstdio>
#include <string>
#include <list>
#include <exception>

#include <pty.h>
#include <sys/select.h>
#include <unistd.h>
#include <fcntl.h>
#include <pthread.h>
#include <errno.h>
#include <signal.h>
#include <string.h>
#include <time.h>
#include <termios.h>
#include <sys/time.h>
#include "tipos.h"

using namespace std;

class ThreadException : public exception {
public:    
    const char* what() const noexcept { return strerror(errno);}
};

class Canal {
public:
    Canal();
    Canal(Options & ops, int fd1, int fd2);
    Canal(const Canal& orig);
    virtual ~Canal();
    int verifica_fila();
    int adiciona_buffer();
private:
    struct Data {
      char buffer[MAXIMO];
      int bytes;

      Data(int bytes, char * ptr) : bytes(bytes) {
          memcpy(buffer, ptr, bytes);
      }
      Data() {}
    };    
    list<Data> txout;
    int fd, dest_fd;
    double atraso;
    double ber;
    int chunk; // quantidade de bytes enviada a cada vez pela serial
    int bitrate;
    pthread_mutex_t mutex;
    pthread_cond_t cond;
    pthread_t tid;
    
    char byte_error() const;
    
    static void* do_tx(void * ptr);
    void run();
};

#endif /* CANAL_H */

