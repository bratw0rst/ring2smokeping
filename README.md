# NLNOG RING Smokeping config generator

This Python script generates Smokeping config containing all NLNOG Ring nodes, 
grouped by country

## How to use
You can either run the script once, or use it regularly with cron

```bash
git clone https://github.com/nickbouwhuis/ring2smokeping
cd ring2smokeping
python3 generate.py
```

The output will be saved to `/tmp/smokeping`. Simply move it to a desirable place
```bash
mv /tmp/smokeping/*.conf /etc/smokeping/config.d/Targets.d/nlnog-ring/
```

add the following to your `Targets` file (in `/etc/smokeping/config.d/Targets`)
```
@include /etc/smokeping/config.d/Targets.d/nlnog-ring/ring.conf
```

and reload smokeping
```bash
systemctl reload smokeping
```

Alternatively, you can place a script like this in your `cron.daily` folder

```bash
#!/bin/bash
python3 /usr/local/src/ring-smokeping-config-generator/generate.py
mv /tmp/smokeping/*.conf /etc/smokeping/config.d/Targets.d/nlnog-ring/
systemctl reload smokeping
```
