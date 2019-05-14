# Lucy
A bot written using discord.py that welcomes people, assigns roles, and posts quotes.

----

DISCLAIMER - I am not an experienced programmer. This code might be unreadable as I never bothered looking up standards, but honestly it's not as much of a spaghetti mess as my usual stuff.

## About the bot:

Lucy was written for use in a single server, and is therefore not equipped to handle multiple servers at once. Make multiple instances of the bot if you need to. As this server used the Dyno bot previously, you will notice many similarities while going over the command list.

Lucy's main features are: Welcoming people who join a server, allowing them to assign roles to themselves, keeping track of people who leave, and posting quotes to a channel. Additionally, if a self-assignable role is renamed, Lucy will automatically update the entry in her list for you, removing the need to do ?delrank oldname and ?addrank newname.

## Commands list:

* **?setchannel [join/leave/quote/commands]** - Depending on which argument was passed, this command will set the current channel as: welcome message channel, leave message channel, quote channel, or commands channel. If the current channel is already a command channel, it'll instead remove it from the list. All other commands can only be used in command channels. - **Owner Only**

* **?welcomemessage [message]** - Sets [message] as the welcoming message Lucy will post when someone new joins the server. Afterwards, it will prompt you for an image link to post along with the message. - Use %u to mention the user - **Owner Only**

* **?goodbyemessage [message]** - Sets [message] as the message Lucy will post when someone leaves the server. - Use %u to add the user's name - **Owner Only**

* **?addrank [role name]** - Adds the role with that name to the list of self-assignable ranks. Role name is case-sensitive. - **Owner Only**

* **?delrank [role name]** - Removes the role with that name from the list of self-assignable ranks. Role name is case-sensitive. - **Owner Only**

* **?editrank [rank name], [join/leave], [message/image]** - Assigns a message/image to be posted when someone joins/leaves a rank with that name. Message and image are independent, but have to be assigned separately. - Use %u to mention the user, and %r to include the rank's name - **Owner Only**

* **?ranks** - Lists all the ranks Lucy can assign to you. (WARNING: If you have a massive amount of ranks, this might break since I never implemented a message buffer)

* **?rank [rank name]** - Either adds or removes a rank with that name from you, depending on whether or not you already have it.

* **?addquote [quote]** - Adds the quote to a list of quotes to be posted periodically. - **Owner Only**

* **?quotes** - Lists all the quotes Lucy can post, along with their position. - **Owner Only**

* **?delquote [position]** - Deletes the quote in a given position. - **Owner Only**
