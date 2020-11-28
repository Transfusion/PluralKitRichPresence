# PluralKitRichPresence
Simple CLI tool to show who's fronting in your Discord Rich Presence

Create an application at https://discord.com/developers/applications, and copy the *CLIENT ID*.
```sh
$ ./pkrpc -id abcde -cid 782147341111111111 -t 20 -h
usage: pkrpc [-h] -id system_id -cid client_id -t interval [-f /path/to/parser.py]
             [-api api_endpoint]

Show your PluralKit fronters in Discord Rich Presence

optional arguments:
  -h, --help            show this help message and exit
  -id system_id, --system_id system_id
                        Your PluralKit System ID
  -cid client_id, --client_id client_id
                        Discord Application Client ID
  -t interval, --interval interval
                        How frequently to poll for updates (in seconds), >= 15
  -f /path/to/parser.py, --fronters_parser /path/to/parser.py
                        Path to a module that contains a function which converts the
                        Fronters API response into the detail and state Rich Presence
                        strings. Example: ./fronters_to_string.py
  -api api_endpoint     PluralKit API Endpoint (default https://api.pluralkit.me)
  ```
  
 
  ![Fronters Info](https://i.imgur.com/Xr1tiCg.png)
