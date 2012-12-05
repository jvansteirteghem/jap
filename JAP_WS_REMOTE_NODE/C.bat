openssl genrsa -out CK.pem 1024
openssl req -new -key CK.pem -out CR.pem -config C.ini
openssl x509 -req -in CR.pem -out C.pem -CA CA.pem -CAkey CAK.pem -CAcreateserial -days 3650 -extensions v3_req -extfile C.ini
pause