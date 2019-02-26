/*
 * To change this license header, choose License Headers in Project Properties.
 * To change this template file, choose Tools | Templates
 * and open the template in the editor.
 */

/* 
 * File:   Pts.cpp
 * Author: msobral
 * 
 * Created on 25 de Agosto de 2017, 13:20
 */

#include "Pts.h"
#include <pty.h>
#include <cstdlib>
#include <strings.h>
#include <errno.h>
#include <string.h>

Pts::Pts() {
  if (openpty(&fd, &sfd, name, NULL, NULL) < 0) {
      throw PtsException(strerror(errno));
  }    
  close(sfd);
  setup_pty();
  if (unlockpt(fd) < 0) throw PtsException(strerror(errno));
}

Pts::Pts(const Pts& orig) {
}

Pts::~Pts() {
}

string Pts::get_slave() const {
    return string(name);
}

// programa a serial (pseudo-terminal mestre)
int Pts::setup_pty() {
  termios oldtio,newtio;

  if (tcgetattr(fd,&oldtio) < 0) throw PtsException(strerror(errno)); 
  bzero(&newtio, sizeof(newtio));
  newtio.c_cflag = CS8 | CLOCAL | CREAD;
  newtio.c_iflag = IGNPAR | IGNBRK;
  newtio.c_oflag = 0;

  newtio.c_cc[VTIME]   = 0;
  newtio.c_cc[VMIN]    = 8;

  tcflush(fd, TCIFLUSH);
  if (tcsetattr(fd,TCSANOW,&newtio) < 0) throw PtsException(strerror(errno));
}

