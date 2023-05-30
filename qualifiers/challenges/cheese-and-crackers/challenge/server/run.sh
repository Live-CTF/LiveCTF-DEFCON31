#!/bin/sh

sed -i "s/LiveCTF{PLACEHOLDER_FLAG}/$FLAG/" .config.toml
#unset FLAG # Server uses env variable

socat TCP-LISTEN:31337,reuseaddr,fork EXEC:./challenge,raw,pty,echo=0
