# homework_bot
### *Description*
A homework_bot accesses the API of the Yandex Practicum and learns the status of the student's homework. In case of a change in the status of the homework, bot informs student in his telegram chat.
### *Technologies*
- Python 3.7
- Python-dotenv 0.19.0
- Python-telegram-bot 13.7
### *How to launch a project*
Create a bot via BotFather account in telegram.

Using terminal change the current working directory to the location where you want the cloned directory.

Clone the repository and go to it:
```
git clone git@github.com:SemenovaLiza/homework_bot.git
```
```
cd homework_bot
```
Install and activate the virtual environment:
```
python -m venv venv
```
```
source venv/bin/activate
```
Install dependencies from the file requirements.txt:
```
python -m pip install --upgrade pip
```
```
pip install -r requirements.txt
```
Create .env file and make in it such variables as:
- A profile token on Yandex Practicum.
- A token of your telegram-bot.
- Your ID in the telegram.
*Example of required variables in an .env file.*
```
PRACTICUM_TOKEN='XXXXX'
TELEGRAM_TOKEN='XXX'
TELEGRAM_CHAT_ID=XXX
```
Run the bot:
```
python homework.py
```
### Author
Semenova Elizaveta
