# Projeto 1: protocolo de enlace

Protocolo destinado a estabelecer enlaces ponto-a-ponto entre computadores. 

### Particularidades:
* Linguagem de programação utilizada: *Python 3*
* Integração ao subsistema de rede do Linux 
* Utilização de um *transceiver* RF como camada física

### As funções do protocolo:
* Enquadramento
* Detecção de erros com CRC-16
* Garantia de entrega com ARQ do tipo pare-e-espere
* Controle de acesso ao meio do tipo Aloha
* Gerenciamento de sessão

## Estrutura do projeto em camadas:

![camadas](https://github.com/mftutui/PTC29008/blob/master/Projeto1-Protocolo-de-Comunicacao/imagens/camadas.png)

## Implementação

De acordo com as especificações adotadas a partir das [discussões em sala de aula](https://wiki.sj.ifsc.edu.br/wiki/index.php/PTC29008:_Projeto_1:_um_protocolo_de_comunica%C3%A7%C3%A3o), o protocolo segue o seguinte padrão:

### Formato de quadro do protocolo

![formato_de_quadro](https://github.com/mftutui/PTC29008/blob/master/Projeto1-Protocolo-de-Comunicacao/imagens/formato_do_quadro.png)

### Gerenciamento de sessão

#### Quadro da camada de gerenciamento de sessão

![quadro_gerenciamento_sessao](https://github.com/mftutui/PTC29008/blob/master/Projeto1-Protocolo-de-Comunicacao/imagens/quadro_gerenciamento_sessao.png)

#### Mensagens de controle

![mensagens_de_controle](https://github.com/mftutui/PTC29008/blob/master/Projeto1-Protocolo-de-Comunicacao/imagens/mensagens_de_controle.png)

Ex: A partir da definição do byte de identificação de mensagens da camada de gerenciamento de sessão chamado ID *PAYLOAD* como 255, ou 11111111 em binário e mensagens não destinadas a esta camada identificadas com 0, ou 00000000 em binário.

Um quadro da camada se sessão enviando uma mensagem de confirmação seria:

![sessao_confirmacao](https://github.com/mftutui/PTC29008/blob/master/Projeto1-Protocolo-de-Comunicacao/imagens/sessao_confirmacao.png)

### Garantia de entrega e controle de acesso ao meio

#### Quadro para garantia de entrega

![garantia_de_entrega](https://github.com/mftutui/PTC29008/blob/master/Projeto1-Protocolo-de-Comunicacao/imagens/grantia_de_entrega.png)

📗 Mais informações podem ser encontradas no [relatório completo](https://github.com/mftutui/PTC29008/blob/master/Projeto1-Protocolo-de-Comunicacao/RELATORIO1_PTC29008.pdf) ou no link [http://protocoloptc.ddnsking.com/](http://protocoloptc.ddnsking.com).

Autores: [Paulo Sell](https://github.com/paulosell) [Maria Fernanda Tutui](https://github.com/mftutui)
