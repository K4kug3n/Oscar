# Oscar

## Presentation

### What & Why
Oscar is a multi-purpose bot developed on-fly for private server.  
Combining useless little things, and some automation, it became a real project that may be cool to have.

### How
Currently Work in Progress section, as Oscar try to improve himself

## Modules 

### Interaction 
Wedding is a fun module. Make Oscar say something (admistrator command) :
> !say #aChannel "a message"  

Oscar can also react to a message (admistrator command) :
> !react #aChannel 00000 :heart:

Status and activity is updated every 10 minutes.  
Need a configuration file `configs/wedding.json` with `married_member: ""` field to start working.

### Wedding
Wedding is a fun module. Link Oscar to a Member of your server with (admistrator command) :
> !marry @yourMember  

Oscar's status & activity will be related to this member, and he will react if pinged by this member  
You can unlink with :  
> !divorce  

Status and activity is updated every 10 minutes.  
Need a configuration file `configs/wedding.json` with `married_member: ""` field to start working.