# Dynamic IP via Yandex PDD DNS hosting

## Config

Store pdd token to .pddtoken file.
After setting address in api, script store last set ip to file .lastip

## WhatMyIp

Scipt can get ip from few services. You can find them in `get_my_ip` function.


## Example

./yaddns.py --host home.example.com


## Example cron record

`
*/10    *    *       *       *       user   /home/user/yaddns/yaddns.py --host home.example.com
`
