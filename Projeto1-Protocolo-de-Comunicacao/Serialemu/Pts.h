/*
 * To change this license header, choose License Headers in Project Properties.
 * To change this template file, choose Tools | Templates
 * and open the template in the editor.
 */

/* 
 * File:   Pts.h
 * Author: msobral
 *
 * Created on 25 de Agosto de 2017, 13:20
 */

#ifndef PTS_H
#define PTS_H

#include <unistd.h>
#include <string>
#include <exception>

using std::string;
using std::exception;

class PtsException : public exception {
public:
    PtsException(const string & arg) : val(arg) {}
    const char* what() const noexcept { return val.c_str();}
  private:
    string val;
};

class Pts {
public:
    Pts();
    Pts(const Pts& orig);
    virtual ~Pts();
    string get_slave() const;
    int get_fd() const { return fd;}
    int get_slave_fd() const { return sfd;}
    void close_slave() {close(sfd);}
private:
    int fd, sfd;
    char name[64];
    
    int setup_pty();
};

#endif /* PTS_H */

