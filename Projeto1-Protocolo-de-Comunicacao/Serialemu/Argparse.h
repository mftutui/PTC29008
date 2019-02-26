/*
 * To change this license header, choose License Headers in Project Properties.
 * To change this template file, choose Tools | Templates
 * and open the template in the editor.
 */

/* 
 * File:   Argparse.h
 * Author: msobral
 *
 * Created on 22 de Agosto de 2017, 16:46
 */

#ifndef ARGPARSE_H
#define ARGPARSE_H

#include <string>
#include <map>
#include <exception>

using namespace std;

class InvalidOption : public exception {
public:
    InvalidOption(const string & opt) : op(opt) {}
    const char* what() const noexcept { return op.c_str();}
  private:
    string op;
};

class InvalidValue : public exception {
public:
    InvalidValue(const string & arg) : val(arg) {}
    const char* what() const noexcept { return val.c_str();}
  private:
    string val;
};

class Argparse {
public:
    Argparse();
    Argparse(const Argparse& orig);
    virtual ~Argparse();

    // Métodos para adicionar uma opção do tipo flag. Tal tipo de opção
    // não requer um valor a ser informado na linha de comando.
    // Ela é do tipo bool: se aparece na linha de comando seu valor é true,    
    // e, caso não apareça, seu valor é false.
    void add_flag(char shortoption);
    void add_flag(const string & longoption);
    
    // Métodos para adicionar uma opção do tipo flag com um valor
    // predefinido
    void add_flag(char shortoption, bool defval);
    void add_flag(const string & longoption, bool defval);
    
    
    // Métodos para adicionar uma opção comum. Tal tipo de opção
    // requer um valor a ser informado na linha de comando.
    // Ela é do tipo string: se aparece na linha de comando, a string que a sucede
    // se torna seu valor. Caso essa opção não apareça, seu valor é uma string vazia.
    void add_option(char shortoption);
    void add_option(const string & longoption);
    
    // Métodos para adicionar uma opção comum com um valor
    // predefinido    
    void add_option(char shortoption, const string & defval);
    void add_option(const string & longoption, const string & defval);
    
    // Métodos para obter o valor de uma opção comum
    string get_option(char shortoption) const;
    string get_option(const string & longoption) const;
    string operator[](const string & longoption) const;
    string operator[](char shortoption) const;

    // Métodos para obter o valor de uma opção do tipo flag
    bool get_flag(char shortoption) const ;
    bool get_flag(const string & longoption) const;
    
    // Método para obter os argumentos que não foram processados como
    // opções.
    string get_extra() const { return extra;}
    
    // Método para analisar os argumentos de linha de comando e extrair
    // as opções e seus valores contidos nesses argumentos. O vetor argv
    // corresponde ao parâmetro argv da função main. A análise das opções
    // é efetuada a partir da segunda posição do vetor (argv[1]).
    int parse(char * argv[]);
private:
    map<string,string> opts;
    map<string,bool> flags;
    string extra; // resto da linha de comando ...
};

#endif /* ARGPARSE_H */

