# Trabalho Sistemas Distribuidos
Trabalho final da disciplina de Sistemas Distribuídos, implementando um serviço de mensageria distribuída utilizando RabbitMQ rodando em Docker dentro de Máquinas Virtuais com Ubuntu. O projeto consiste em um Producer e um Consumer que se comunicam por meio de filas de mensagens.

## Descrição
Este projeto simula a comunicação entre duas máquinas virtuais (VMs) por meio de filas de mensagens, utilizando o RabbitMQ como serviço de mensageria. A máquina virtual VM1 age como um Producer, enviando mensagens que são recebidas pela máquina virtual VM2, que atua como Consumer. As mensagens são transmitidas através de diferentes exchanges (direct, fanout, topic), possibilitando vários tipos de roteamento de mensagens.

## Tecnologias Utilizadas
RabbitMQ: Broker de mensagens usado para comunicação entre os serviços.
Docker: Contêineres utilizados para rodar o RabbitMQ.
Python: Linguagem usada no Consumer.
Node.js: Linguagem usada no Producer.
Pika: Biblioteca Python para integrar o RabbitMQ com o Consumer.
Express: Framework web usado no Producer com Node.js.
PyQt: Framework para criar a interface gráfica no Consumer.

## Pré-requisitos
Certifique-se de ter os seguintes componentes instalados no ambiente de desenvolvimento:

Docker e Docker Compose
Node.js (para o Producer)
Python 3.x e pip (para o Consumer)
RabbitMQ (executando em contêiner Docker)
Dependências de cada máquina virtual (detalhadas abaixo)

## Arquitetura do Sistema
- Producer (VM1 - principal.js): Envia mensagens para o RabbitMQ através de exchanges e filas, utilizando diferentes padrões de roteamento (direct, fanout, topic).
- Consumer (VM2 - chat2.py): Recebe as mensagens das filas e as exibe em uma interface gráfica simples feita com PyQt.
- A comunicação é feita através de RabbitMQ, que atua como intermediário na troca de mensagens entre as VMs.

## Referências
[RabbitMQ][https://www.rabbitmq.com/]
[Docker][https://www.docker.com/]
[Node.js][https://nodejs.org/pt]
[Python Pika][https://pika.readthedocs.io/en/stable/]
