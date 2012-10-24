openssl genrsa -des3 -out CAK.pem 2048
openssl req -new -x509 -days 3650 -key CAK.pem -out CA.pem -config CA.ini
pause