# Protocolo para bate-papo

Aplicação de bate papo desenvolvida na disciplica de *Projeto de protocolos*

## Sumário

* [Especificação do serviço](#especificação-do-serviço)
* [Vocabulário](#vocabulário)
* [Manual de uso](#manual-de-uso)


## Especificação do serviço

A aplicação de bate papo foi desenvolvida a partir do modelo cliente/servidor usando sockets. 

O programa servidor assim que inicializado, cria um socket utilizando a função socket() e a partir da função bind() associa o socket a uma porta do sistema operacional. Em seguida aguarda a conexão de clientes nessa mesma porta utilizando listen(). 

Quando um cliente faz uma conexão, a chamada accept() é utilizada do lado do servidor a fim de estabelecer a comunicação entre ambos. Em seguida o cliente se conecta ao servidor através da função connect() e inicia um loop para a troca de mensagens através do par de funções sen () e recv(). O mesmo loop é estabelecido no lado do servidor, esperando novas conexões com a função listem(), bem como a troca de mensagens também utilizando as chamadas send() e recv(). 

- O serviço nao possui restrições qundo a sistemas operacionais para implementado.

- A aplicação foi desenvolvida utilizando a linguagem de programação *Python 2.7.10* o que carreta na necessidade da instalação do mesmo para o uso do bate papo.

- O bate papo foi feito com base em: [chat-app](https://github.com/Rishija/chat-app)

## Vocabulário  

 - A aplicação do servidor conta com uma série de funções para a troca de mensagens. Cada mensagem vinda do cliente é tratada no servidor e de acordo com o seu conteúdo. Tendo como exemplo, mensagens cujo conteúdo não possui nenhuma palavra reservada são enviadas utilizando a função *send_to_all()* para todos os clinetes conectados ao chat. Todas as funções encontradas no *servidor.py* serão descritas a seguir:

*send_to_all(sock, message)*
- A função é responsável por enviar uma mensagem para todos os clientes conectados, exeto para o clinete que está solicitando o envio.

*private_guide(sock)*
- A fim de alertar um cliente sobre a sintaxe correta para o envio de uma mensagem privada a função é responsável por mostrar ao próprio clinete como fazê-lo.

*check_name_list(conn, record, suport, connected_list)*
- A cada novo usuário conectado ao chat é feito o teste para saber se o nome de identificação escolhido pelo mesmo já existe no chat, o que é feito a partir da varredura dos dicionários de controle. Caso o usuário tenha um nome único no sistema o mesmo é inicializado no babe papo, caso contrário, a conexão é encerrada.

*show_users(sock, suport, your_name)*
- Para facilitar o envio de uma mensagem privada o usuário dispõe de uma função que mostra todos os usuários conectados ao servidor. A função faz a varredura em um dicionário de controle e plota os nomes dos conectados. 

*private_msg(data, sock, suport)*
- Utilizando o objeto de socket de quem solicitou o envio de uma mensagem privada, a função separa as informações provenientes do dado enviado pelo cliente e faz o envio da mensagem para o usuário especificado. Além de chamar a função *private_guide(sock)* caso a sintaxe esteja errada.

*welcome_rules(conn)*
- Função carregada após a conexão do usuário para apresentação das palavras reservadas e suas funções. 

*exit_chat(sock, name_ex, record, suport, connected_list)*
- A parir do uso da palavra "exit" o clinete pode sair do chat e enviar uma mensagem informando os demais conectados. Essa função também é responsável por remover as informações do cliente desconectado dos dicionários de controle. O socket é encerrado no cliente.

- Assim como em *server.py* a aplicação do lado cliente, *client.py* possui funções para serem utilizadas de acordo com a necessidade do clinete. As funções do cliente serão descritas a seguir:

*display()*
- Função utilizada para mostrar "You:" sempre que o usuário estiver aguardando para enviar ou receber uma mensagem. 

*check_name_empty()*
- Verifica se o username informado pelo cliente no inicio da conexão é válido, possui algum caracter.

*exit_char(client_socket)*
- Função responsável pela desconexão de um clinete que enviou a mensagem "exit" para o servidor. 

## Manual de uso

### Servidor

O bate papo deve ser inicializado com o servidor.

*Server*
> $ python server.py
<pre>
	SERVER WORKING 
</pre>

### Cliente

Após, poderão ser inicializados os clientes de forma similar ao servidor.

*Client*
> $ python client.py
<pre>
    Enter username:
</pre>

O mesmo procedimento deverá ser realizado para cada um dos clientes que desejarem participar do chat.

Antes de tudo, é necessário informar um nome de usuário. O mesmo não deverá ser nulo ou já estar cadastrado no bate papo.

*Client*
<pre>
Enter username: Maria
Welcome to chat room! 
- Enter 'exit' anytime to left. 
- Enter 'show users' to see who is online. 
- To send a private message use: 'p.USERNAME:msgContent'
</pre>


Uma mensagem é impressa no servidor para o controle dos usuários cadastrados

*Server*
<pre>
Client (127.0.0.1, 51640) connected [ Maria ]
</pre>

Caso o servidor não tenha sido inicializado uma mensagem será enviada ao cliente, onformando-o.

*Client*
<pre>
Enter username: Maria
Can't connect to the server.
</pre>

Caso seja usado um nome já escolhido. O usuário será desconectado.

*Client*
<pre>
Enter username: Maria
Username already taken! 
YOU ARE DISCONNECTED!!
</pre>

Caso o nome seja completo com espaços ou não possua caracteres, o usuáro será questionado novamente.

*Client*
<pre>
Enter username: 
Username is empty!
Enter username: 
</pre>

Assim que outros usuários entrares no bate papo uma mensagem informando a inclusão dos mesmos será envida a cada um dos usuários já conectados.

*Client*
<pre>
...
The user Ana joined the conversation. 
</pre>

Inicialmente todas as mensagem trocadas são publicas, ou seja, todos os demais usuários conectados receberão.

A fim de visualizar todos os usuários logados o usuário pode, a qualquer momento enviar "show users" e uma lista com os nomes será apresentada.

*Client*
<pre>
...
You: show users
Connected users: 
- Clara
- Ana
- Frida
You: 
</pre>

Se o usuário for o único online no momento a seguinte mensagem será apresentada.

*Client*
<pre>
...
You: show users
There are no users connected besides you.
You: 
</pre>

Para o envio de mensagens privadas deverá ser usada a seguinte sintaxe: p.USERNAME:msgContent

- O cliente deverá iniciar a mensagem com *.p*, em seguida colocar o nome do usuário para o qual deseja enviar a mensagem, *Clara*, logo após acrescentar dois pontos *:* e a mensagem a ser enviada.

*Client*
<pre>
...
You: p.Clara:Mensagem privada!!
Your private message was sended.
You: 
</pre>

Se o usuário escolhido estiver conectado no momento, a mensagem será envida.

*Client*
<pre>
...
Private message from Maria: Mensagem privada!!
You: 
</pre>

O servidor será notificado sobre o envio da mensagem da seguinte forma:

*Server*
<pre>
Client (127.0.0.1, 51640) [ Maria ] sending a private message to: [ Clara ]
</pre>

Caso contrário, uma mensagem informado que o usuário não encontra-se conectado será apresentada.

*Client*
<pre>
...
You: p.Fernanda:Nova mensagem privada!!
The user Fernanda is not connected. 
You:
</pre> 

Nesse caso o servidor só receberá uma notificação de mensagem comum.

*Server*
<pre>
Data [ p.Fernanda:Nova mensagem privada!! ] received from: [ Maria ]
</pre>

Quanto ao envido da mensagem privada, se a sintaxe da mesma estiver diferente da prevista será apresentada a sintaxe correta para o usuário.

*Client*
<pre>
...
You: p.
Wrong sintaxe! 
To send a private message use: 'p.USERNAME:msgContent'
You: 
</pre> 

ou

<pre>
...
You: p.Clara
Wrong sintaxe! 
To send a private message use: 'p.USERNAME:msgContent'
You: 
</pre>

Para sair do chat o cliente por a qualquer momento enviar "exit", assim que enviado o clinete será desconectado do chat. Todos os usuários ainda conectados receberão uma mensagem informando a saída do usuário.

*Client*
<pre>
...
You: exit
</pre>

*Client*
<pre>
...
The user Clara left the conversation. 
You: 
</pre>

Da mesma forma, o servidor será notificado.

*Server*
<pre>
Client (127.0.0.1, 51667) is offline (error) [ Clara ]
</pre>

Caso o servidor seja derrubado, todos os usuários serã autimaticamente desconectados e apresentarão a seguinte mensagem:

*Client*
<pre>
...
YOU ARE DISCONNECTED!! 
</pre>

Cada mensagem enviada por um clinete, será mostrada no console do sevidor como forma de controle de mensagem e confirmação de recepção. 

*Server*
<pre>
Client (127.0.0.1, 51640) connected [ Maria ]
Data [ show users ] received from: [ Maria ]
Client (127.0.0.1, 51659) connected [ Ana ]
Client (127.0.0.1, 51667) connected [ Clara ]
Client (127.0.0.1, 51640) [ Maria ] sending a private message to: [ Clara ]
Data [ exit ] received from: [ Maria ]
Client (127.0.0.1, 51667) is offline (error) [ Maria ]
Data [ exit ] received from: [ Clara ]
Client (127.0.0.1, 51667) is offline (error) [ Clara ]
</pre>
