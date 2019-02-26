/*
 * To change this license header, choose License Headers in Project Properties.
 * To change this template file, choose Tools | Templates
 * and open the template in the editor.
 */

/* 
 * File:   tipos.h
 * Author: msobral
 *
 * Created on 25 de Agosto de 2017, 12:57
 */

#ifndef TIPOS_H
#define TIPOS_H

// Tamanho maximo de buffer
const int MAXIMO=4096;

// menor atraso possivel ... 10 ms
const int TIMEOUT=10000 ;

// periodo entre transmissoes pela serial, em microssegundos
const int PERIODO_TX=10000;

struct Options {
  double atraso;
  double ber;
  int chunk; // quantidade de bytes enviada a cada vez pela serial
  int bitrate;
  int bg;
};



#endif /* TIPOS_H */

