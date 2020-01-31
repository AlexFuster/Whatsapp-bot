# Whatsapp-bot
I use python with selenium to create a bot with access to whatsapp web. It can read and send messages, send photos, videos and audios  
The good thing about this one is that it cannot be easily detected by Whatsapp. Most of bots are made by reverse engineering the requests made by the whatsapp application. This produces bots that are very easy to use, but at the cost of receaving a ban after an update made by Whatsapp.  
By using, selenium, one can have a reliable whatsapp bot for personal use. This bot just interacts with the Whatsapp web interface (like a human does), so the requests are built by the frontend itself, not by the bot. This makes the bot very stable and difficult to ban.

Getting started:
* Make an excel file called rules.xlsx following the format specified below and save it to the same location as whatsbot2.py 
* run whatsbot2.py with your python3 interpreter 
* click the "init driver" button
* Use your phone to scan the QR code and actually enter Whatsapp web
* Click the "activate bot" button. Now the bot is running. It is not recommended to use the same Whatsapp web session than the bot while it is active.
* Click the "deactivate bot" button. now the bot activity is paused.
* Modify the rule sheet rules.xlsx
* Click the "load rule sheet" button to reload the rules sheet
* Click the "activate bot" button to see the new rules in action.
* Click the "deactivate bot" button.
* Click the "close whatsapp" button.
* Click the "Quit" button.

rules.xlsx format:


|Conversation|Author|Time|Text|Answer|
|---|---|---|---|---|
||||hello|Hello|
|girlfriend|||i love you|I love you too|
|group of friends|bestfriend||plan|I'm in!!|

Empty cells are wildcards. In case of collision, the bot answers the most specific row. For a rule to match, all of its cells must be contained in the incoming message metadata. This means that "Hello, how're you doing" will trigger the first rule, as it contains "hello". This is the dumb rule-based system bot that I made. Feel free to improve it :)
