# Scrapper Tool

Scraps some tutorial info from the tutorial URL.

Uses:

* selenium
* BeautifulSoup4

## Install

### Linux

#### Geckodriver (Firefox)

https://github.com/mozilla/geckodriver/releases/latest

```sh
# install firefox
sudo apt install firefox-esr

# install geckodriver
./get_linux_geckodriver.fish
```

#### Chromedriver (Chrome)

* install chrome from Google
* download chromedriver from https://sites.google.com/chromium.org/driver/downloads

```sh
# install chrome
wget https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb
sudo apt install ./google-chrome-stable_current_amd64.deb
rm ./google-chrome-stable_current_amd64.deb

# install chromedriver
./get_linux_chromedriver.fish
```
