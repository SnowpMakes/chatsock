# chatsock
A simple python TCP socket server, hosting a low-level chat service

## What is it?
Well, it's a python program that you run, which hosts a simple chat server. Users can connect, and they can chat live.

Chat messages are sent to other members immediately, without the message being saved on the server. No messages are logged in any way.
Messages are only stored on the server in the form of "message history", to send to the client when a new message is about to arrive. This "message history" will never contain more than `"chatviewMax"` ([Check "Configuration"](#Configuration)) messages.

**Please note: This server does NOT run on an encrypted protocol, which means if someone manages to put themselves inbetween the connection, they can read ALL communications between client and server!**

(There might come an encrypted ssh version of this server in the future.)

## Running
Download the zip, or run `git clone https://github.com/SnowpMakes/chatsock`, and then start the server using `python3 chatsock.py`. You can then stop the server by pressing `ctrl+c`. The server will then broadcast about the shutdown, disconnect all users, and shut down exactly 5 seconds later.

## List of (future) features
* Server:
  * Full control over the server settings
  * Custom welcome message
  * Server shutdown message to all clients
* Chatrooms:
  * Public chatrooms
  * Limit the number of users in that chatroom at a time
* Command palette:
  * Use commands to navigate your way around the chat server
  * Use `:join` to join a chatroom, and then execute `:chat` to enter chat view
* Chatview:
  * A live view of the messages being sent in a chatroom
  * Enables you to send messages to that chatroom yourself
  * No commands are availiable in chatview. Execute `:q` to return to the command palette
  * (Not yet implemented) Messages are planned to have a 150 character limit.
  
**Future stuff:**
* DMs:
  * Will enable users to have private conversations
* Password protected / Hidden chatrooms:
  * Will be a password protected chatroom, which does not show up in `:rooms`. You will need to know the name and the password in order to join
* User accounts: (Far future version)
  * Will enable users to really identify eachother, knowing that there is only one person with that username. Now you can just choose any username, as long as there is no user online with the same name.
  * Will probably log you in using a little webserver you have to connect to using HTTPS..? Feels like a little bit overkill though.

## Configuration
chatsock was created with configurability in mind. You can configure the server without having to have any knowledge about programming.

Around the top of `chatsock.py` there is a big block named `CONFIG`, within this block you can configure the server:
* `"port"`: The port the server will run on. Please note chat choosing a port < 1024 will require you to start the server as admin. The server will then be started on <ip-address>:<port>
* `"rooms"`: The chatrooms availiable:
  * `"<name of chatroom>"`: The name of the chatroom, with inside of it, some settings:
    * `"public"`: Either `True` or `False`. Determines whether the channel will show up when the command `:rooms` is executed. If a channel is not public (`False`), the `password` field must be set to a password required to join the room. But for now, if a channel is not public (`False`), the channel is not accessible to anyone. Not even if you know the password (this will be fixed in a future version).
    * `"password"` (only required if `public` is set to `False`)(NOT WORKING YET): The password required to join the chatroom. If the password is set to nothing (`""`), the chatroom won't be accessible AT ALL!
    * `"description"`: A short description for the chatroom, shown when `:rooms` is executed.
    * `"limit"`: The maximum number of people allowed in the chatroom at once. Set to `0` to have no limit.
* `"welcomeMessage"`: A welcome message shown when a user initially joins.
* `"connectionTimeout"`: Either `True` or `False`. Set to `True` to force the user to wait for 2.5 seconds, to prevent instantly reconnecting / trying to DDOS
* `"chatviewMax"`: The maximum number of messages in the chat history of every client. This will also determine the height of the chatview
* `"usernameLimit"`: The maximum length of a username.

## Commands
When connected, users can execute commands to, for example, join a chatroom. Here follows a list of currently existing commands in chatsock:
* `:help`: Show this list
* `:list`: List all users in the current chatroom / DM
* `:listall`: List all users online
* `:rooms`: List all availiable chatrooms
* `:join <chatroom>`: Join chatroom with the name `<chatroom>`
* `:dm <user>`: Open a DM with user <user> **NOT IMPLEMENTED YET**
* `:chat`: When connected to a chatroom / DM, enter chatview. Use `:q` to quit
* `:close`: Close your connection with the current chatroom (Leave the current chatroom)
* `:quit`: Close your connection with the chat server entirely
