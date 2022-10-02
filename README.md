# twitter_bot
A twitter bot that reads the message after the associated twitter account is mentioned, reads through a google sheets file and if the sender's account is present in the google sheets file, returns a meme image.

This project uses the twitter api to interact with twitter and the python gspread module to interact with google sheets.

Requirement:
  - Twitter api access and credentions
  - Gspread python module
  - Google cloud project api and credentials
  
You will also need several image files (named accordingly i.e image1.jpg, image2.jpg etc in the project folder) to be twitted as response.
  
Example:
A twitter account mentions the bot account @{twitter_bot_username} {insert specified command here}


P.S: This project was hosted with heroku but can also be hosted with AWS or Google cloud.
