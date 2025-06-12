The bot is built using python and the aim is to perform analysis on accounts in order to determine if they are trustworthy in the Web3 space.
To run this bot locally you should have the following: Twitter development account, python 3.7+, pip manager, or you could just use replit online.
A .env file where all your secrets and API keys will be stored, these secrets can be found in the developer account.
The project structure will look like this. X-bot/ analyzer.py, fallback_accounts.py, main.py, replier.py, requirements.txt, trust_check.py, trusted_accounts.py.
The requirements.txt contains all the dependencies and can be installed locally using pip install -r requirements.txt .
The trusted_accounts.py contains the logic to get the trusted accounts automatically from github and if that fails it uses the provided list in the fallback_accounts.py
The analyzer.py contains the logic to analyze the account under which the bot was mentioned.
The replier.py contains the logic to reply the account after successful analysis of the account in question.
The trust_check.py contains the logic for checking if the account is trustworthy or not based on number of followers it has in common to the trusted account list. If it has more than 2 it is trustworthy and vice versa.
The main.py contains is where everything comes together and works as an entity for the bot to function.
To run the bot locally run python main.py on the terminal after installing all dependencies.
To run the bot online, use replit(follow instructions on the site).


