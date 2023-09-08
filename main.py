from keep_alive import keep_alive
import os
import aiohttp
import discord

API_URL = 'https://api-inference.huggingface.co/models/imuncomfortable/'

class MyClient(discord.Client):
    def __init__(self, model_name):
        intents = discord.Intents.default()
        intents.message_content = True
        super().__init__(intents=intents)
        self.api_endpoint = API_URL + model_name
        huggingface_token = os.environ['HUGGINGFACE_TOKEN']
        self.request_headers = {
            'Authorization': 'Bearer {}'.format(huggingface_token)
        }

    async def query(self, payload):
        """
        Make an asynchronous request to the Hugging Face model API
        """
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(self.api_endpoint, headers=self.request_headers, json=payload) as response:
                    ret = await response.json()
                    return ret
        except aiohttp.ClientResponseError as e:
            # Handle API error
            return {'error': str(e)}

    async def on_ready(self):
        print('Logged in as')
        print(self.user.name)
        print(self.user.id)
        print('------')
        await self.query({'inputs': {'text': 'Hello!'}})

    async def on_message(self, message):
        if message.author.id == self.user.id:
            return

        payload = {'inputs': {'text': message.content}}

        async with message.channel.typing():
            response = await self.query(payload)

        bot_response = response.get('generated_text', None)

        if not bot_response:
            if 'error' in response:
                bot_response = '`Error: {}`'.format(response['error'])
            else:
                print(response)
                bot_response = 'Hmm... something is not right.'

        await message.channel.send(bot_response)


def main():
    client = MyClient('DiabloGPT-small-CocoAtarashi')

    try:
        keep_alive()
        client.run(os.environ['DISCORD_TOKEN'])
    except discord.errors.HTTPException as e:
        if e.code == 429:
            print("\n\n\nToo Many Requests (Error code 429) occurred\nRESTARTING NOW\n\n\n")
            # Restart the bot by executing 'kill 1' command
            os.system('kill 1')
        else:
            raise e


if __name__ == '__main__':
    main()
