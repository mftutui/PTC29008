#include <stdio.h>
#include <pty.h>
#include <sys/select.h>
#include <unistd.h>
#include <stdlib.h>
#include <fcntl.h>
#include <pthread.h>
#include <errno.h>
#include <signal.h>
#include <string.h>
#include <time.h>
#include <termios.h>

// Tamanho maximo de buffer
#define MAXIMO 4096

// menor atraso possivel ... 10 ms
#define TIMEOUT 10000 

// periodo entre transmissoes pela serial, em microssegundos
#define PERIODO_TX 10000

//#define LOG

#ifdef LOG
FILE * logf;
#endif

pthread_mutex_t mutex;
pthread_cond_t cond;

typedef struct NODO Nodo;

struct NODO {
  char buffer[MAXIMO];
  int bytes;
  int fd;
  double time;
  Nodo * proximo;
};

typedef struct {
  Nodo * primeiro;
  Nodo * ultimo;
} Lista;

struct Options {
  double atraso;
  double ber;
  int chunk; // quantidade de bytes enviada a cada vez pela serial
  int bitrate;
  int bg;
  int fd[2];
  Lista * f1, * f2;
};

void ajuda(char * path) {
  printf("Uso: %s [-b BER][-a atraso][-f][-B taxa_bits] | -h\n", path);
  printf("\nBER: taxa de erro de bit, que deve estar no intervalo  [0,1]\n");
  printf("atraso: atraso de propagação, em milissegundos.\n");
  printf("taxa_bits: taxa de bits em bits/segundo\n");
  printf("-f: executa em primeiro plano (nao faz fork)\n\n");
}

// programa a serial (pseudo-terminal mestre)
int setup_pty(int fd) {
  struct termios oldtio,newtio;

  tcgetattr(fd,&oldtio);
  bzero(&newtio, sizeof(newtio));
  newtio.c_cflag = CS8 | CLOCAL | CREAD;
  newtio.c_iflag = IGNPAR | IGNBRK;
  newtio.c_oflag = 0;

  newtio.c_cc[VTIME]   = 0;
  newtio.c_cc[VMIN]    = 8;

  tcflush(fd, TCIFLUSH);
  tcsetattr(fd,TCSANOW,&newtio);
}

// gera um byte com uma mascara de erro aleatoria
char byte_error(double ber) {
  int n = 0;
  char r = 0;
  int bit;
  static seeded = 0;

  if (ber == 0) return  0;

  if (! seeded) {
    srand48(time(NULL));
    seeded = 1;
  }

  for (n=0, bit=1; n < 8; n++, bit = bit<<1) {
    if (drand48() <= ber) {
      r += bit;
    }
  }
  return  r;
}

// Funcoes para manipular as filas de chunks recebidos dos pseudo-terminais mestres (seriais)

// Cria uma fila
Lista * cria_lista() {
  Lista * p = (Lista*)malloc(sizeof(Lista));
  p->primeiro = p->ultimo = NULL;
  return  p;
}

// Testa se fila está vazia
int lista_vazia(Lista * f) {
  return (f->primeiro == NULL);
}

// Adiciona um nodo ao fim da fila
void adiciona_nodo(Lista  * f) {
  struct timeval tv;

  Nodo * p = (Nodo*)malloc(sizeof(Nodo));

  p->proximo = NULL;
  p->bytes = 0;
  gettimeofday(&tv, NULL);
  p->time = tv.tv_sec + tv.tv_usec*1e-6;

  if (f->ultimo == NULL) {
    f->ultimo = p;
    f->primeiro = p;
  } else {
    f->ultimo->proximo = p;
    f->ultimo = p;
  }  
}

// Remove um nodo da frente da fila (acho que nem uso mais essa funcao ...)
void remove_frente(Lista * f) {
  Nodo  * p, * ptr;
  
  if (f->primeiro == NULL) return;
  p = f->ultimo;
  if (f->primeiro == f->ultimo) {
    free(p);
    f->ultimo = NULL;
    f->primeiro = NULL;
    return;
  }
  for (ptr = f->primeiro;  ptr->proximo != p; ptr=ptr->proximo);
  ptr->proximo = NULL;
  f->ultimo = ptr;
  free(p);
}

// Verifica se ha um chunk na fila que possa ser enviado.
// confere se o atraso de propagacao foi cumprido.
int verifica_fila(Lista * f) {
  struct timeval tv;
  int n = 0;
  Nodo * p;
  
  pthread_mutex_lock(&mutex);

  if (f->primeiro == NULL) {
    pthread_mutex_unlock(&mutex);
    return 0;
  }
  gettimeofday(&tv, NULL);
#ifdef LOG
  fprintf(logf, "fila: primeiro=%p, ", f->primeiro);
  fprintf(logf, "bytes=%d, delta=%lg\n", f->primeiro->bytes, tv.tv_sec + tv.tv_usec*1e-6 - f->primeiro->time);
  fflush(logf);
#endif

  if (tv.tv_sec + tv.tv_usec*1e-6 >= f->primeiro->time) {
    int bytes;
    char * ptr;
    int limite = f->primeiro->bytes;

    ptr = f->primeiro->buffer;
    while (limite > 0) {
      bytes = write(f->primeiro->fd,  ptr, limite);
      if (bytes < 0) break; // erro ???
      limite -= bytes;
      ptr += bytes;
    }
    if (bytes > 0) n += f->primeiro->bytes;
    p = f->primeiro;
    f->primeiro = f->primeiro->proximo;
    free(p);
    if (f->primeiro == NULL) {
      f->ultimo = NULL;
    }
  }

  pthread_mutex_unlock(&mutex);

  return  n;
}

// Adiciona um chunk na fila, aplicando os erros de bit aleatorios
int adiciona_buffer(Lista * f, int fd, int dest_fd, struct Options * opcoes) {
  int bytes=0, n, aChunk = opcoes->chunk;
  char * ptr;
  int limite = MAXIMO;
  char buffer[MAXIMO];

  // Le bytes da linha serial
  if ((bytes = read(fd, buffer, limite)) <= 0) {
    return 0;
  }

  // Aplica erros de transmissao aleatorios
  if (opcoes->ber > 0) {
    for (n=0; n < bytes; n++) {
      buffer[n] = buffer[n] ^ byte_error(opcoes->ber);
    }
  }

  // Guarda os bytes recebidos em pedacos de ateh "opcoes->chunk" bytes
  pthread_mutex_lock(&mutex);
  for (n=0; n < bytes; n += opcoes->chunk) {
    if (n + aChunk > bytes) aChunk = bytes - n;
    adiciona_nodo(f);
    f->ultimo->fd = dest_fd;
    f->ultimo->time += opcoes->atraso;
    f->ultimo->bytes = aChunk;
    memcpy(f->ultimo->buffer, buffer + n, aChunk);
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
void * do_tx(void * ptr) {
  struct Options * opcoes = (struct Options*) ptr;
  struct timeval t1, t2;
  struct timespec tr, tm;
  int dt;
  //double dtx = 0;
  int n1 = 0, n2 = 0;

  while (1) {
    pthread_mutex_lock(&mutex);
    if (lista_vazia(opcoes->f1) && lista_vazia(opcoes->f2)) {
      //printf("esperando ...\n");
      pthread_cond_wait(&cond, &mutex);
    }
    pthread_mutex_unlock(&mutex);
    gettimeofday(&t1, NULL);
    //dtx = (t1.tv_sec - t2.tv_sec) + (t1.tv_usec - t2.tv_usec)*1e-6;
    //fprintf(stderr,"intervalo: %lf, %lf, %lf\n", dtx, n1/dtx, n2/dtx);
    n1 = verifica_fila(opcoes->f1);
    n2 = verifica_fila(opcoes->f2);
    gettimeofday(&t2, NULL);
    dt = (t2.tv_sec - t1.tv_sec)*1000000 + (t2.tv_usec - t1.tv_usec);
#ifdef LOG
    fprintf(logf, "verifica_fila: %d bytes, e vai dormir %d microssegundos\n", n1+n2, PERIODO_TX - dt);
    fflush(logf);
#endif
    if (dt <= PERIODO_TX) {
      //printf("dt=%d, PERIODO_TX=%d\n", dt, PERIODO_TX);
      tr.tv_sec = 0;
      tr.tv_nsec = (PERIODO_TX - dt)*1000;
      nanosleep(&tr, &tm);
    }
  }
  pthread_exit(NULL);
}

// interpreta as opções de linha de comando
int parse_args(int argc, char **argv, struct Options * opcoes) {
  char * opcao = "b:a:B:fh";
  int  atraso;
  char op;

  opcoes->atraso = 0;
  opcoes->ber = 0;
  opcoes->bg = 1;
  opcoes->bitrate = 0;
  opcoes->chunk = MAXIMO;
  opterr = 0;

  while ((op = getopt(argc, argv, opcao)) >= 0) {
    switch (op) {
      case 'f':
        opcoes->bg = 0;
        break;
      case 'b':
        if (sscanf(optarg, "%lg", &opcoes->ber) < 1) {
          printf("Erro: opção -b requer um valor real para BER (taxa de erro de bit)\n");
          return 0;
        }
        if ((opcoes->ber < 0) || (opcoes->ber > 1)) {
          printf("Erro: BER (taxa de erro de bit) deve estar no intervalo [0,1]\n");
          return 0;
        }
        break;
      case 'B':
        if (sscanf(optarg, "%d", &opcoes->bitrate) < 1) {
          printf("Erro: opção -B requer um valor inteiro para taxa de bits (em bits/segundo)\n");
          return 0;
        }
        if (opcoes->bitrate <= 0) {
          printf("Erro: taxa de bits deve ser > 0\n");
          return 0;
        }
        opcoes->chunk = (opcoes->bitrate * (PERIODO_TX*1e-6))/8;
        break;
      case 'a':
        if (sscanf(optarg, "%d", &atraso) < 1) {
          printf("Erro: opção -a requer um valor inteiro (atraso em milissegundos)\n");
          return 0;
        }
        if (atraso < 0) {
          printf("Erro: atraso deve ser > 0\n");
          return 0;
        }
        opcoes->atraso = atraso*1e-3;
        break;
      case 'h':
        ajuda(argv[0]);
        return 0;
        break;
      default:
        ajuda(argv[0]);
        return  0;
        break;
    }
  }
  return  1;
}

int main(int argc, char ** argv) {
  fd_set rfds, wfds;
  char s1[64], s2[64];
  char * slave[2] = {s1, s2};
  int sfd[2];
  int n;
  char c;
  int fop;
  struct Options opcoes;
  struct timeval timeout;
  pthread_t tid;

  if (! parse_args(argc, argv, &opcoes)) return  0;

  //printf("rate=%d, chunk=%d\n", opcoes.bitrate, opcoes.chunk);
  //return 0;

  // cria os dois pseudo-terminais, mostrando seus pathnames na tela
  openpty(&opcoes.fd[0], &sfd[0], slave[0], NULL, NULL);
  openpty(&opcoes.fd[1], &sfd[1], slave[1], NULL, NULL);
  printf("%s %s\n", slave[1], slave[0]);

  // fecha os escravos (aqui nao serao necessarios)
  close(sfd[0]);
  close(sfd[1]);

  // define a configuracao dos pseudo-terminais (parecida com portas seriais)
  setup_pty(opcoes.fd[0]);
  setup_pty(opcoes.fd[1]);

  // se for para rodar como daemon, vai pra 2o plano ...
  if (opcoes.bg) {
    if (fork()) {
      return 0;
    }
  }

#ifdef LOG
  logf = fopen("se.log", "w");
#endif

  // cria as filas de saida de cada pseudo-terminal
  opcoes.f1 = cria_lista();
  opcoes.f2 = cria_lista();

  // Mutex para manipular as filas de saida
  pthread_mutex_init(&mutex, NULL);
  pthread_cond_init(&cond, NULL);

  // Cria tarefa de envio periodico, que envia um chunk a cada PERIODO_TX
  if (pthread_create(&tid, NULL, do_tx, (void*)&opcoes)) {
    perror("Ao criar a thread de transmissao ...");
    return errno;
  }

  // laco principal: espera chegar algo por ao menos um dos pseudo-terminais, e entao
  // adiciona os chunks recebidos na fila de saida do outro pseudo-terminal
  while (1) {
    FD_ZERO(&rfds);
    FD_ZERO(&wfds);
    FD_SET(opcoes.fd[0], &rfds);
    FD_SET(opcoes.fd[1], &rfds);
    n = select(opcoes.fd[1]+1, &rfds, NULL, NULL,  NULL);

    if (n > 0) {
      if (FD_ISSET(opcoes.fd[0], &rfds)) {
        int bytes = adiciona_buffer(opcoes.f1, opcoes.fd[0], opcoes.fd[1], &opcoes);
#ifdef LOG
        fprintf(logf, "0 -> 1: %d\n", bytes);
        fflush(logf);
#endif
      }
      if (FD_ISSET(opcoes.fd[1], &rfds)) {
        int bytes = adiciona_buffer(opcoes.f2, opcoes.fd[1], opcoes.fd[0], &opcoes);
#ifdef LOG
        fprintf(logf, "1 -> 0: %d\n", bytes);
        fflush(logf);
#endif
      }
    } else {
      perror("");
      break;
    }
  }

  pthread_kill(tid, SIGKILL);

}

