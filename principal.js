const amqp = require('amqplib/callback_api');
const readline = require('readline');


const rl = readline.createInterface({
    input: process.stdin,
    output: process.stdout
});

amqp.connect('amqp://localhost', (err, conn) => {
    if (err) {
        throw err;
    }

    conn.createChannel((err, ch) => {
        if (err) {
            throw err;
        }

        const promptUser = () => {
            rl.question('Escolha o tipo de exchange (direct, fanout, topic): ', (exchangeType) => {
                if (!['direct', 'fanout', 'topic'].includes(exchangeType)) {
                    console.log('Tipo de exchange invalido');
                    return promptUser();
                }
        
                rl.question('Digite a mensagem: ', (msg) => {
                    if (exchangeType === 'direct' || exchangeType === 'topic') {
                        rl.question('Digite as chaves de roteamento (separadas por vírgula): ', (routingKeysInput) => {
                            const routingKeys = routingKeysInput.split(',').map(key => key.trim());
                            sendMessage(ch, exchangeType, msg, routingKeys);
                            promptUser();
                        });
                    } else {
                        sendMessage(ch, exchangeType, msg);
                        promptUser();
                    }
                });
            });
        };

        const sendMessage = (channel, exchangeType, msg, routingKeys = ['']) => {
            const exchange = exchangeType === 'direct' ? 'direct_logs' :
                             exchangeType === 'fanout' ? 'logs' : 'topic_logs';
        
            channel.assertExchange(exchange, exchangeType, { durable: false });
            routingKeys.forEach((routingKey) => {
                channel.publish(exchange, routingKey, Buffer.from(msg));
                console.log(` [x] Enviou ${exchangeType} com a mensagem: '${msg}' e chave de roteamento: '${routingKey}'`);
            });
        };

        promptUser();
    });
});

rl.on('close', () => {
    process.exit(0);
})