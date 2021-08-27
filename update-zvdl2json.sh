cd /usr/src/zvdl2json || exit
git pull
cp zvdl2json.py /opt/zvdl2json
chmod +x /opt/zvdl2json/zvdl2json.py
cp zvdl2json.service /etc/systemd/system/zvdl2json.service
systemctl daemon-reload
systemctl restart zvdl2json && systemctl status zvdl2json