92.242.58.199:5245
IP во внутренней сети вышки - 172.18.198.36:22
IP внутри VPN - 192.168.14.216:22
remote name: marsohod.auditory.ru
old remote name: vpn14.on-air.pro
Логин/пароль - marsohod/mars0h0d
Конфиг для подключения к VPN и SSH-ключ для авторизации на сервере прилагаю
pass-phrase SSH-ключа - marsohod

https://askubuntu.com/questions/284276/how-can-connect-server-using-ppk-key-file

ssh -i marsohod.key marsohod@192.168.14.216
ssh -i marsohod.ppk -p 5245 marsohod@92.242.58.199
