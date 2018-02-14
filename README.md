<b>HOW TO INSTALL:

If you're so inclined go ahead and create a seperate environment (the only dependency is requests so this probably isn't necessary)

Be sure to use Python >= 3.4

Then run:
`pip install -r requirements.txt`

You're done :)

<b>HOW TO USE:

Open a command line / terminal / shell window and navigate to the folder containing scraper.py

Run `python scraper.py start_time=<> num_days=<> coin=<>`

Example: `python scraper.py start_time=1514764800 num_days=10 coin=bitcoin`

Each argument is required

`start_time` -- the start timestamp of the data to grab (unix timestamp, use https://www.epochconverter.com/ and be sure to use the one WITHOUT milliseconds)

`num_days` -- the number of days of data to grab after the start time

`coin` -- the name of the coin to pull data for according to coinmarketcap's URL for the coin (for https://coinmarketcap.com/currencies/zcash/ use zcash)

Please don't play with the sleep time in the call_api function or coinmarketcap WILL BAN YOU WITHOUT WARNING OR HESITATION and more importantly maybe even change their endpoint so this script will break
