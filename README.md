# Oscar

## Presentation

### What & Why
Oscar is a multi-purpose bot developed on-fly for private server.  
Combining useless little things, and some automation, it became a real project that may be cool to have.

### How
Currently Work in Progress section, as Oscar try to improve himself

## Modules 

### Interaction 
Interaction is a fun module. Make Oscar say something (admistrator command) :
> !say #aChannel "a message"  

Oscar can also react to a message (admistrator command) :
> !react #aChannel 00000 :heart:

### Wedding
Wedding is a fun module. Link Oscar to a Member of your server with (admistrator command) :
> !marry @yourMember  

Oscar's status & activity will be related to this member, and he will react if pinged by this member  
You can unlink with :  
> !divorce  

Status and activity is updated every 10 minutes.  
Need a configuration file `configs/wedding.json` with `married_member: ""` field to start working.

### Instagram
Instagram is a automation module. Oscar will post a message if a new publication is posted on configurated accounts.
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