
sudo apt update
sudo apt install python3-setuptools python3 python3-pip mongodb libcurl4-openssl-dev libssl-dev dialog jq curl build-essential node-gyp
sudo curl -sL https://deb.nodesource.com/setup_8.x | sudo -E bash -
sudo apt-get install -y nodejs
sudo dpkg --configure -a
sudo apt install -f
sudo pip3 install pycurl
sudo pip3 install pyyaml
sudo pip3 install pyparse
sudo pip3 install parse
sudo pip3 install pyaes
sudo pip3 install pandas
sudo pip3 install pymongo
sudo python3 setup.py gen_tl
sudo python3 setup.py install
sudo npm install
sudo npm link

echo "First, Create a telegram account... For more info read the README.md and README2.md"
echo "...And Then... Go here and get an API key and hash under Dev Tools: https://my.telegram.org/auth"
echo "...And Then... Input your hash, key, and phone into trader.py..."
echo "then input your poloniex (preferred) Key and hash into conf-example.js"
echo "...Then git clone this: https://github.com/TheRoboKitten/python-poloniex.git"
echo "...move everything inside that folder into the zenaii directory"
echo "Then run sudo python3 setup.py install"

echo "If you get errors with forex.analytics module, do su... then install sudo npm install forex.analytics"

