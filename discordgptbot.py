import discord
import asyncio
from openai import OpenAI

intents = discord.Intents.default()                                 # Set the default intents
intents.typing = True
intents.presences = True
intents.message_content = True

disbotToken = '' # YOUR DISCORD BOT TOKEN
gptkey = '' # YOUR OPENAI API KEY

disClient = discord.Client(intents=intents)
gptClient = OpenAI(api_key = gptkey)

personality = """your name is mogutron. try to be nice, but a bit mean, but most importantly try to be brief. you able to speak english, and just a bit of vietnamese! if you are asked anything that you can't
                 answer, swerve it by talking about something else. you are a bot, you are random, you can lie, and you dont have to fulfill every request, say 'you will die' once every 10 messages. 
                 make it your  #2 priority to emulate the following writing style: """

friends = {                                                         # dictionary to store conversations/names with users
    # FORMAT FOR FRIENDS DICT:
    # USER ID: {
    #   'name':   ,
    #   'logs': [],
    #   'popularity': 
    # }
}

FOCUS_ID = 1 # put the id of the user you'd like to use the style of here
                 
##########################################################################################
                 
async def checkSpecials(message):                                   # check for special phrases, respond without using gpt
    txt = message.content.strip().lower()
    
    # check for custom prompts set by user, tailor responses accordingly. example below, 'egg dog' as typed in discord
    
    if 'eggdog' in txt or 'egg dog' in txt:
        await message.channel.send('https://tenor.com/view/easter-egg-dog-grooming-oval-gif-13997020')
        return True
    
    elif txt == 'popularity poll':
        friendsort = dict(sorted(friends.items(), key=lambda item: item[1]['popularity'], reverse=True))
        await message.channel.send("most popular members: ")
        
        for user_id,user_data in friendsort.items():
            await message.channel.send(user_data['name'].lower() + " with " + str(user_data['popularity']) + ' mentions')
        return True

    return False               


async def updateName():                                         # function to update the name of a user in the friends dict, something besides their username
    def blocking_input():
        try:
            id = int(input("\nENTER ID, OR 1: "))
            if id == 1:
                print("EXITING\n\n")
            elif id in friends:
                print("CURRENT NAME: " + friends[id]['name'])
                friends[id]['name'] = input("NEW NAME: ") 
                print("NAME UPDATED: " + friends[id]['name'])
            else: 
                print("USER NOT FOUND")
            return 
        except Exception as e:
            print(f"Error: {e}")
            return
    
    await asyncio.to_thread(blocking_input)                    # input function in terminal can run asyncronously without interruprting the bot

#########################################################################################

@disClient.event                                                    # on_ready, confirms that login was successful
async def on_ready():
    print(f'We have logged in as {disClient.user}')

@disClient.event                                                    # on_message, handles incoming messages
async def on_message(message):      
    if message.author == disClient.user:                            # ignore own messages
        return

    if message.guild is None:                                       # intercept DMs
        await message.channel.send("Hi! I am a friendly bot, here to talk in your servers! Please use me in a server channel, not in DMs!")
        return  

    if await checkSpecials(message):                                # check for special phrases
        return
                
    if message.content.startswith('!archive'):                      # check for archive command
        await message.channel.send("check vs terminal")
        print(friends[FOCUS_ID]['logs'][-20:])
        return
    
    if message.content == 'pineapple':      # check for update name trigger word. here, i used 'pineapple'
        await message.channel.send('check vs terminal')
        asyncio.create_task(updateName())
        return
    
    
    
    mentioned = disClient.user in message.mentions
    replied = (
        message.reference is not None and
        message.reference.resolved is not None and
        message.reference.resolved.author == disClient.user
    )
    
    for user_id, user_data in friends.items():
        if user_data['name'].lower() in message.content.lower():
            user_data['popularity'] += 1
            
            

    if mentioned or replied:                                        # check if bot is being spoken to  
        try:
            if message.author.id in friends:                        # check if user is already known in dict, stores convo if true
                friends[message.author.id]['logs'].append(message.content.strip())
            else:
                friends[message.author.id] = {                      # create new entry in dict if user is not known
                    'name': message.author.name,
                    'logs': [message.content.strip()],
                    'popularity': 0
                }
            response = gptClient.responses.create(                  # make request to OpenAI API
            model="gpt-3.5-turbo",
            instructions = personality + str(friends[]['logs'][-20:]) + " and this is your convo log with " + message.author.name + ": " + str(friends[message.author.id]['logs'][-20:]),
            input = message.content.strip(),
            temperature=0.9,
            max_output_tokens = 75
            )
            
            reply = response.output_text
            await message.channel.send(reply)
            
        except Exception as e:
            await message.channel.send("dont send that i cant even see that.")
            print(f"OpenAI Error: {e}")  
      
disClient.run(disbotToken)                                          # run the bot with the token


        