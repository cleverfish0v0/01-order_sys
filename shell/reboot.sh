

echo -e "\033[34m--------------------wsgi process--------------------\033[0m"

ps -ef|grep uwsgi_order_sys.ini | grep -v grep

sleep 0.5

echo -e '\n--------------------going to close--------------------'

ps -ef |grep uwsgi_order_sys.ini | grep -v grep | awk '{print $2}' | xargs kill -9

sleep 0.5

echo -e '\n----------check if the kill action is correct----------'

/envs/order_sys/bin/uwsgi --ini /data/www/01-order_sys/shell/uwsgi_order_sys.ini >/dev/null &

echo -e '\n\033[42;1m----------------------started...----------------------\033[0m'
sleep 1

ps -ef |grep uwsgi_order_sys.ini | grep -v grep