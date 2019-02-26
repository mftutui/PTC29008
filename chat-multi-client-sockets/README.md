# Protocolo para bate-papo

Aplicação de bate papo desenvolvida na disciplica de *Projeto de protocolos*

## Manual de uso

### Inicialização Cliente/Servidor

## Servidor

A inicialização é feita a partir do servidor.

**Server**
> $ python server.py
<pre>
				SERVER WORKING 
</pre>

## Cliente

Após, poderão ser inicializados os clientes de forma similar ao servidor.

**Client**
> $ python client.py
<pre>
    Enter username:
</pre>

O mesmo procedimento deverá ser realizado para cada um dos clientes que desejarem participar do chat.

Antes de tudo, é necessário informar um nome de usuário. O mesmo não deverá ser nulo ou já estar cadastrado no bate papo.

**Client**
<pre>
    Enter username: Maria
    Welcome to chat room! 
    - Enter 'exit' anytime to left. 
    - Enter 'show users' to see who is online. 
    - To send a private message use: 'p.USERNAME:msgContent'
</pre>

Caso o servidor não tenha sido inicializado uma mensagem será enviada ao cliente, onformando-o.

**Client**
<pre>
    Enter username: Maria
    Can't connect to the server.
</pre>

Caso seja usado um nome já escolhido. O usuário será desconectado.

**Client**
<pre>
    Enter username: Maria
    Username already taken! 
    YOU ARE DISCONNECTED!!
</pre>

Caso o nome seja completo com espaços ou não possua caracteres, o usuáro será questionado novamente.

**Client**
<pre>
    Enter username: 
    Username is empty!
    Enter username: 
</pre>

Assim que outros usuários entrares no bate papo uma mensagem informando a inclusão dos mesmos será envida a cada um dos usuários já conectados.

**Client**
<pre>
    ...
    The user Ana joined the conversation. 
</pre>

Inicialmente todas as mensagem trocadas são publicas, ou seja, todos os demais usuários conectados receberão.

A fim de visualizar todos os usuários logados no momento o usuário pode, a qualquer momento enviar "show users". Uma lista com os nomes será apresentada.

**Client**
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

**Client**
<pre>
    ...
    You: show users
    There are no users connected besides you.
    You: 
</pre>

Para o envio de mensagens privadas deverá ser usada a seguinte sintaxe: p.USERNAME:msgContent

- O cliente deverá iniciar a mensagem com *.p*, em seguida colocar o nome do usuário para o qual deseja enviar a mensagem, *Clara*, logo após acrescentar dois pontos *:* e a mensagem a ser enviada.

**Client**
<pre>
    ...
    You: p.Clara:Mensagem privada!!
    Your private message was sended.
    You: 
</pre>

Se o usuário escolhido estiver conectado no momento, a mensagem será envida.

**Client**
<pre>
    ...
    Private message from Maria: Mensagem privada!!
    You: 
</pre>

Caso contrário, uma mensagem informado que o usuário não encontra-se conectado será apresentada.

**Client**
<pre>
    ...
    You: p.Fernanda:Nova mensagem privada!!
    The user Fernanda is not connected. 
    You:
</pre> 

Quanto ao envido da mensagem privada, se a sintaxe da mesma estiver diferente da prevista será apresentada a sintaxe correta para o usuário.

**Client**
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

**Client**
<pre>
    ...
    You: exit
</pre>


**Client**
<pre>
    ...
    The user Clara left the conversation. 
    You: 
</pre>

Caso o servidor seja derrubado, todos os usuários serã autimaticamente desconectados e apresentarão a seguinte mensagem:

**Client**
<pre>
    ...
    YOU ARE DISCONNECTED!! 
</pre>