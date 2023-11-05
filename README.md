# SunBot
SunBot is a Discord bot that provides current and upcoming weather information for thousands of locations around the world.

## Installation 

In order to install the project, you can firstly create an environment using following commands. The `SunBot` project require python 3.8+, but python 3.10 is the recommanded version.
```
conda create -n sunbot python==3.10
conda activate sunbot
```
Then clone the project using ssh protocol:
```
git clone git@github.com:clement-pages/SunBot.git
```

This project uses [Poetry](https://python-poetry.org) as packages and dependencies management tool. Type the following commands:
* Install `poetry`
```
sudo apt update
sudo apt install python3-poetry
```
* Resolve and install project's dependencies:
```
poetry install
```

The `SunBot` bot is deployed on a [fly.io](https://fly.io/) server. The `main` branch of this github repository is automatically deployed on a `fly.io` server using continuous integration. But a deployment can
be done manually using `flyctl` command. Most generally, this command allows to control the application direclty in command lines from a terminal. In order to use this tool, you need to have a `fly.io` account and 
an access to the bot application server: 

* Type the following commands to install `flyctl`:
```
curl -L https://fly.io/install.sh | sh
```
* Add these two lines to your `.bashrc` file by replacing `user-name` by your user name:
```
echo 'export FLYCTL_INSTALL="/home/<user-name>/.fly"' >> ~/.bashrc  
echo 'export PATH="$FLYCTL_INSTALL/bin:$PATH"' >> ~/.bashrc
```
* If you don't have an account, sign up using following command:
```
fly auth signup
```
* Then you can connect to your account:
```
fly auth login
```
* To deploy manually the app, use the command below:
```
fly deploy
```
Your environment is almost ready! The final step is to set environment variables (for example in your .bashrc file) to launch the bot from your computer. Claim value for these variables (for team members only)! These variables
are used to access to the visual crossing API and to connect the bot to discord.

## Useful links:

* [Discord API documentation](https://discordpy.readthedocs.io/en/stable/api.html)
* [Visual Crossing](https://www.visualcrossing.com/)
