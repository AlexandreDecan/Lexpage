#!/bin/bash
set -e
set -x

for i in firefox google-chrome google-chrome-stable chromium-browser
do
    echo removing ${i}...
    sudo rm -f $(which $i) || echo "nope ..."
done

if [[ "${BROWSER:0:13}" == "google-chrome" ]]
then
  wget -q -O - https://dl-ssl.google.com/linux/linux_signing_key.pub | sudo apt-key add -
  echo "deb http://dl.google.com/linux/chrome/deb/ stable main" | sudo tee /etc/apt/sources.list.d/google.list
fi

if [[ "$BROWSER" == "phantomjs" ]]
then
    : PhantomJS is already installed
elif [[ "$BROWSER" == "firefox-aurora" ]]
then
    pip uninstall -y selenium
    pip install http://ethylix.be/~roidelapluie/selenium-2.48.0-py3-none-any.whl
    wget https://github.com/jgraham/wires/releases/download/v0.5.0/wires-0.5.0-linux64.gz -O - | zcat | sudo tee /usr/bin/wires > /dev/null
    sudo chmod +x /usr/bin/wires
    yes|sudo add-apt-repository ppa:ubuntu-mozilla-daily/firefox-aurora
    sudo apt-get -qq update
    sudo apt-get -qq install firefox
elif [[ "$BROWSER" == "firefox-esr" ]] || [[ "$BROWSER" == "firefox-beta" ]]
then
    sudo apt-get remove -qq firefox
    wget -O - "https://download.mozilla.org/?product=${BROWSER}-latest&os=linux64&lang=en-US" | sudo tar xjf - -C /opt
    sudo ln -s /opt/firefox/firefox /usr/bin/firefox
else
    sudo apt-get install -qq $BROWSER
fi

if [[ "$BROWSER" == "chromium-browser" ]] || [[ "${BROWSER:0:13}" == "google-chrome" ]]
then
    wget https://chromedriver.storage.googleapis.com/2.20/chromedriver_linux64.zip
    unzip chromedriver_linux64.zip
    sudo mv chromedriver /usr/bin
fi
