/*
 * To change this license header, choose License Headers in Project Properties.
 * To change this template file, choose Tools | Templates
 * and open the template in the editor.
 */

/* 
 * File:   Argparse.cpp
 * Author: msobral
 * 
 * Created on 22 de Agosto de 2017, 16:46
 */

#include "Argparse.h"

Argparse::Argparse() {
}

Argparse::Argparse(const Argparse& orig) {
    opts = orig.opts;
}

Argparse::~Argparse() {    
}

void Argparse::add_option(const string& longoption) {
    add_option(longoption, "");
}

void Argparse::add_option(char shortoption) {
    add_option(shortoption, "");
}

void Argparse::add_option(const string& longoption, const string& defval) {
    string option = longoption;
    
    if (option.size() == 1) option.insert(0, 1, '-');
    else option.insert(0, 2, '-');
    
    if (opts.count(option) > 0) throw InvalidOption(option); // erro: opção já cadastrada
    opts[option] = defval;
}

void Argparse::add_option(char shortoption, const string& defval) {
    string op;
    op += shortoption;
    add_option(op, defval);
}

void Argparse::add_flag(const string& longoption) {
    add_flag(longoption, false);
}

void Argparse::add_flag(char shortoption) {
    add_flag(shortoption, false);
}

void Argparse::add_flag(const string& longoption, bool defval) {
    string option = longoption;
    
    if (option.size() == 1) option.insert(0, 1, '-');
    else option.insert(0, 2, '-');
    
    if (opts.count(option) > 0) throw InvalidOption(option); // erro: opção já cadastrada
    flags[option] = defval;
}

void Argparse::add_flag(char shortoption, bool defval) {
    string op;
    op += shortoption;
    add_flag(op, defval);
}

bool Argparse::get_flag(char shortoption) const {
    string op;
    op += shortoption;

    return get_flag(op);
}

bool Argparse::get_flag(const string & longoption) const {
    string option = longoption;
    
    if (option.size() == 1) option.insert(0, 1, '-');
    else option.insert(0, 2, '-');

    try {
        return flags.at(option);
    } catch (...) {
        throw InvalidOption(option); // flag inválida
    }
}

string Argparse::get_option(char shortoption) const {
    string op;
    op += shortoption;

    return get_option(op);
}

string Argparse::get_option(const string & longoption) const {
    string option = longoption;
    
    if (option.size() == 1) option.insert(0, 1, '-');
    else option.insert(0, 2, '-');

    try {
        return opts.at(option);
    } catch (...) {
        throw InvalidOption(option); // opção inválida
    }
}

string Argparse::operator [](const string& longoption) const {
    return get_option(longoption);
}

string Argparse::operator [](char shortoption) const {
    return get_option(shortoption);
}

int Argparse::parse(char* argv[]) {
    int n = 1, cnt = 0;
    int state = 1;
    string op;
    
    while (argv[n]) {
        switch (state) {
            case 1: { // espera uma opção
                op = argv[n];
                if (op[0] != '-') { // final das opções ???
                    int k = n;
                    for (; argv[k] != NULL; k++) {
                        extra += argv[k];
                        extra += ' ';
                    }
                    return n;
                }
                auto jt = flags.find(op);
                if (jt != flags.end()) { // encontrou uma flag
                    jt->second = true;
                } else {
                    auto it = opts.find(op);
                    if (it == opts.end()) throw InvalidOption(op); // opção inválida
                    state = 2;
                }
                break;
            }
            case 2: { // espera um argumento da opção anterior
                string val = argv[n];
                if (val[0] == '-') throw InvalidValue(val); // argumento não pode iniciar com hifen
                auto p = opts.find(op);
                p->second = val;
                //opts[op] = val;
                state = 1;
                cnt++;
            }
        }
        n++;
    }
    return cnt;
}
