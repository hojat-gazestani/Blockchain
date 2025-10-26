# digital signature 

private to public Asymmetric encryption hash

+ creating digital signature 
+ Data validation using digital signature 
+ Fraud detection using digital signature 

## creating digital signature

Hello world-> Hash(hello world) -> encrypt the hash value using private key 

figure 13-1 page 132

## Data validation using digital signature

in reciver 
Decrypt the encrypted part using public key-> hash value
the hash value == message's hash

figure 13-2 page 135


## Fraud detection using digital signature
in reciver 
Decrypt the encrypted part using public key-> hash value
the hash value != message's hash

figure 13-3 page 135


