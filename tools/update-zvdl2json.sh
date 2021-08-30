cd /usr/src/zvdl2json || exit
git pull
cp zvdl2json.py /opt/zvdl2json
chmod +x /opt/zvdl2json/zvdl2json.py
systemctl restart zvdl2json && systemctl status zvdl2json