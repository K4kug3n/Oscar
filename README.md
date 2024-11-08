# Oscar

## Presentation

### What & Why
Oscar is a multi-purpose bot developed on-fly for private server.  
Combining useless little things, and some automation, it became a real project that is absolutely necessary (not sure).

### How
Currently Work in Progress section, as Oscar try to improve himself

The minimal setup is to add `configs/config.json` file in the Oscar folder, with it inside : 
```
{
	"token": "XX",
	"active_modules": []
}
```

You need to replace XX with your bot token. Modules are desactivated by default, add there names (in lowercase) in `active_modules` to activate them on Oscar reboot.  

You can also use command to configure actives modules (administrator commands) :
> !module list  
> !module load name  
> !module unload name  

## Modules 

### Interaction 
Interaction is a fun module. Make Oscar say something (administrator command) :
> !say #aChannel "a message"  

Oscar can also react to a message (admistrator command) :
> !react #aChannel 00000 :heart:

### Wedding
Wedding is a fun module. Link Oscar to a Member of your server with (administrator command) :
> !marry @yourMember  

Oscar's status & activity will be related to this member, and he will react if pinged by this member  
You can unlink with :  
> !divorce  

Status and activity is updated every 10 minutes.  
Need a configuration file `configs/wedding.json` with `married_member: ""` field to start working.

### Quote
Quote is a fun module. Make Oscar look intelligente by quoting things. Add you quote in `configs/quotes.csv` with `,` splitter.  
Oscar will pick one to say with (administrator command) : 
> !quote say  

### Voice
Voice is a fun module. Make Oscar join & quit in voice channels (administrator commands) :
> !voice join <#aVoiceChannelId>  
> !voice quit  

While connected, Oscar can play audio file placed in `sounds/` with (administrator commands) :
> !voice play "file.mp3"  

Also, Oscar can play automated sound on certain event with `configs/voice.json` file : 
```
{
	"on_join":{
		"active": true,
		"type": "RANDOM",
		"names": [ "Hello1.mp3", "Hello2.mp3" ]
	},
	"on_quit":{
		"active": true,
		"type": "SINGLE",
		"name": "Bye.mp3"
	},
	"on_ping":{
		"active": true,
		"type": "SINGLE",
		"name": "Ping.mp3"
	}
}
```
With `"type": "SINGLE"`, the sound specified will be played. The `"type": "RANDOM"` will pick one of the random specified sounds.  

*Warning* FFMPEG should be installed and `ffmpeg` should be in the PATH to make Voice module work.

### Welcome

Welcome is an automation module. Oscar will post a message if a new member join.
Currently, the setup only depends on configuration file `configs/welcome.json` : 
```
{
	"welcome_channel": XXXXXXXXXXXXX,
    "default_role_ids": [],

	"buttons_roles": [
		{
			"emoji":  "0️⃣",
			"roles": []
		},
		{
			"emoji": "1️⃣",
			"roles": []
		}
	],

	"welcome_message":{
		"content": "Welcome",
		"content_args": []
	}
}
```
`welcome_channel` need to be filled with your welcome channel (where the message will be posted).    
`default_role_ids` contains id of default role given when joining the server.  
`buttons_roles` contains the different infos about boutons added to the welcome message, it can give role when clicked.  
`welcome_message` field will be detailed later (still WIP)  

It's possible to try the setup with (administrator command) : 
>!welcome @aMember  

Which will post the welcome message for this member in the current channel.

### Instagram
Instagram is an automation module. Oscar will post a message if a new publication is posted on configurated accounts.
Currently, the setup only depends on configuration file `configs/instagram.json` :  
```
{
    "media_endpoint": "https://graph.instagram.com/me/media?fields=id,media_url,username,caption,timestamp,permalink&access_token=",
    "refresh_endpoint": "https://graph.instagram.com/refresh_access_token?grant_type=ig_refresh_token&access_token=",
    "accounts": [
        {
            "name": "MyAccount",
            "message": {
                "content": "Hello {ping}",
                "arguments": [
                    {
                        "name": "ping",
                        "type": "DISCORD:ROLE:PING",
                        "id_role": XXXXXXXXXXXXXXXXX
                    }
                ]
            },
            "token":"XXX",
            "token_expires_date": 0,
            "token_next_update_date": 0,
            "published_ids": [],
            "channel_id": XXXXXXXXXXXXXXXXXX
        }
    ]
}
```
You need to replace XX with revelant infos to add your first instagram account to Oscar (refer to Meta documentation for `token` field). Add other accounts in `accounts` field with the same partern.  

`message` field will be detailed later (still WIP), you can currently ping a role when posting.  

*Warning* Be ready for a spam on first use, Oscar will post about every post found before registering them (you can add there id's as string in `published_ids` to prevent it).

### Gumroad  
Gumroad is an automation module. Oscar will post a message if a new product is published on configurated accounts.
Currently, the setup only depends on configuration file `configs/gumroad.json` :  
```
{
    "endpoint": "https://api.gumroad.com/v2/products?access_token=",
    "accounts": [
        {
            "product_channel_id": XXXXXXXXXXXXXXXXXX,
            "token": "XXX",
            "published_ids": []
        }
    ]
}
```
You need to replace XX with revelant infos to add your first instagram account to Oscar (refer to Gumroad documentation for `token` field). Add other accounts in `accounts` field with the same partern.  

`message` field will be added later (still WIP).

*Warning* Be ready for a spam on first use, Oscar will post about every product found before registering them (you can add there id's as string in `published_ids` to prevent it).