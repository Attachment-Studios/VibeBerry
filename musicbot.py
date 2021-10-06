# Music Bot

import youtubesearchpython
import pytube
import discord
import nacl

import os

async def reply(ctx, text:str):
	embed = discord.Embed(
		title = "Help",
		color = 0x05cfde,
		description = "VibeBerry is a music bot."
	)
	embed.set_thumbnail(
		url='https://images-ext-2.discordapp.net/external/B3fan6_20nbG7ZQRdpRYKxTJcOQrASTBj75hN97IgUE/%3Fsize%3D1024/https/cdn.discordapp.com/avatars/895121185065562184/9e3b25a9f265d9c4de656df3aeffd5d5.webp'
	)

	embed.set_footer(
		text = "Services under Berry Foundations - Attachment Studios",
		icon_url = "https://images-ext-1.discordapp.net/external/x_dF_ppBthHmRPQi75iuRXLMfK0wuAW2sBLTdtNlXAc/%3Fsize%3D1024/https/cdn.discordapp.com/avatars/894098855220617216/d9b9a3b48a054b9847401bb9178ed438.webp"
	)

	embed.add_field(
		name = 'Alert!',
		value = text
	)

	await ctx.channel.send(embed=embed)

def download_video(video:dict):
	yt_video = pytube.YouTube(video['link'])
	video_streams = yt_video.streams.filter(progressive=True).order_by("resolution")
	video_streams[-1].download()

async def connect(ctx):
	dm_connection = ctx.channel.type == discord.ChannelType.private
	
	if dm_connection:
		await reply(ctx, 'This command is exclusive to servers only.')
	else:
		voiceState = ctx.author.voice
		if voiceState == None:
			await reply(ctx, 'Please connect to a voice/stage channel in the server.')
			return 'no continue'
		else:
			channel = voiceState.channel
			await channel.connect()
			await reply(ctx, f'Connected to <#{channel.id}>.')

async def disconnect(ctx):
	dm_connection = ctx.channel.type == discord.ChannelType.private

	if dm_connection:
		await reply(ctx, 'This command is exclusive to servers only.')
	else:
		voiceState = ctx.guild.me.voice
		if voiceState == None:
			await reply(ctx, 'Connected to no voice/stage channels.')
		else:
			channel = voiceState.channel
			voiceClient = ctx.guild.voice_client
			await voiceClient.disconnect()
			await reply(ctx, f'Disconnected from <#{channel.id}>.')

async def play(ctx, command_input:str):
	dm_connection = ctx.channel.type == discord.ChannelType.private

	if dm_connection:
		await reply(ctx, 'This command is exclusive to servers only.')
	else:
		voiceState = ctx.guild.me.voice
		if voiceState == None:
			continue_function = await connect(ctx)
			if continue_function == 'no continue':
				return
		
		if command_input.replace(" ", "") == "":
			await reply(ctx, 'Please provide a valid input like video name or url on YouTube.')
		else:
			video = video_search(str(command_input))
			
			await reply(ctx, f'Downloading and playing `{video["title"]}`. This may take a few seconds or minutes. Be patient.')
			
			for file in os.listdir('.'):
				if file.endswith('.mp4'):
					os.remove(file)
			
			download_video(video)
			
			title = ""
			for ch in video['title'].lower():
				if ch in 'abcdefghijklmnopqrstuvwxyz 1234567890':
					title += str(ch)
				else:
					title += str(' ')
			
			while not(os.path.isfile(f'{title}.mp4')):
				for file in os.listdir('.'):
					if file.endswith('.mp4'):
						os.rename(file, f'{title}.mp4')
			
			try:
				voiceClient = ctx.guild.voice_client
				if voiceClient.isPlaying():
					await voiceClient.stop()
				await voiceClient.play(discord.FFmpegPCMAudio(f"{title}.mp4"))
			except Exception as e:
				print(e)

async def pause(ctx):
	dm_connection = ctx.channel.type == discord.ChannelType.private

	if dm_connection:
		await reply(ctx, 'This command is exclusive to servers only.')
	else:
		voiceState = ctx.guild.me.voice
		if voiceState == None:
			await reply(ctx, 'Can not pause. Not playing any music.')
		else:
			voiceClient = ctx.guild.voice_client
			if voiceClient.is_playing():
				voiceClient.pause()
				await reply(ctx, 'Paused music.')
			else:
				await reply(ctx, 'Can not pause. Not playing any music.')

async def resume(ctx):
	dm_connection = ctx.channel.type == discord.ChannelType.private

	if dm_connection:
		await reply(ctx, 'This command is exclusive to servers only.')
	else:
		voiceState = ctx.guild.me.voice
		if voiceState == None:
			await reply(ctx, 'Can not resume. Not paused any music.')
		else:
			voiceClient = ctx.guild.voice_client
			if voiceClient.is_paused():
				voiceClient.resume()
				await reply(ctx, 'Resumed music.')
			else:
				await reply(ctx, 'Can not resume. Not paused any music.')

async def stop(ctx):
	dm_connection = ctx.channel.type == discord.ChannelType.private

	if dm_connection:
		await reply(ctx, 'This command is exclusive to servers only.')
	else:
		voiceState = ctx.guild.me.voice
		if voiceState == None:
			await reply(ctx, 'Can not stop. Not playing any music.')
		else:
			voiceClient = ctx.guild.voice_client
			if voiceClient.is_playing():
				voiceClient.stop()
				await reply(ctx, 'Stopped music.')
			else:
				await reply(ctx, 'Can not stop. Not playing any music.')

def video_search(query:str):
	video_search = youtubesearchpython.VideosSearch(str(query), limit = 1)
	video_raw_data = video_search.result()['result'][0]
	
	video_data = {}
	required_entities = [
		'title',
		'duration',
		'link'
	]
	
	for data_type in video_raw_data:
		if str(data_type) in required_entities:
			video_data.update(
				{
					str(data_type) : str(video_raw_data[data_type])
				}
			)
	
	return video_data

async def trigger(ctx, command:str, command_input:str):
	if command == "connect":
		await connect(ctx)
	elif command == "disconnect":
		await disconnect(ctx)
	elif command == "play":
		await play(ctx, command_input)
	elif command == "pause":
		await pause(ctx)
	elif command == "resume":
		await resume(ctx)
	elif command == "stop":
		await stop(ctx)

