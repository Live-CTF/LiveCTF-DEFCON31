#!/bin/sh

echo LiveCTF\{"$FLAG"\} > /flag
unset FLAG

#nsjail --config nsjail.conf
socat TCP-LISTEN:31337,reuseaddr,fork EXEC:./challenge,raw,pty,echo=0
