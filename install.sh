#! /bin/bash

installSoftware() {
    apt -qq -y install python3-flask python3-click uwsgi-plugin-python3 python3-pip nginx git
}

installMyStocks() {
    mkdir -p /var/log/uwsgi
    pip3 install -e git+https://github.com/sunshineplan/MyStocks.git#egg=bookmark --src /var/www
}

setupsystemd() {
    cp -s /var/www/stock/stock.service /etc/systemd/system
    systemctl enable stock
    service stock start
}

writeLogrotateScrip() {
    if [ ! -f '/etc/logrotate.d/uwsgi' ]; then
        cat >/etc/logrotate.d/uwsgi <<-EOF
		/var/log/uwsgi/*.log {
		    copytruncate
		    rotate 12
		    compress
		    delaycompress
		    missingok
		    notifempty
		}
		EOF
    fi
}

createCronTask() {
    cp -s /var/www/stock/BackupMyStocks /etc/cron.monthly
    chmod +x /var/www/stock/BackupMyStocks
}

setupNGINX() {
    cp -s /var/www/stock/MyStocks.conf /etc/nginx/conf.d
    sed -i "s/\$domain/$domain/" /var/www/stock/MyStocks.conf
    service nginx reload
}

main() {
    read -p 'Please enter domain:' domain
    installSoftware
    installMyStocks
    setupsystemd
    writeLogrotateScrip
    createCronTask
    setupNGINX
}

main
