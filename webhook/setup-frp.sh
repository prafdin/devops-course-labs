#!/bin/bash

PROXY=course.prafdin.ru
TOKEN=devops
ID=kiselev
SSH_PORT=3146

sudo tee /etc/frp/frpc.toml > /dev/null <<EOF
serverAddr = "$PROXY"
serverPort = 7000
auth.method = "token"
auth.token = "$TOKEN"

[[proxies]]
name = "app-$ID"
type = "http"
localPort = 8181
customDomains = ["app.$ID.$PROXY"]

[[proxies]]
name = "ssh-$ID"
type = "tcp"
localPort = 22
remotePort = $SSH_PORT
EOF

sudo systemctl restart frpc

ssh -p $SSH_PORT $USER@$PROXY