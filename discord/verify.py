import discord
import logging
from discord import app_commands
import json
from xrpl.asyncio.clients import AsyncWebsocketClient
from xrpl.models.requests import AccountLines, AccountNFTs
import xumm
import gspread
import asyncio

logging.basicConfig(level=logging.INFO)

class aclient(discord.Client):
    def __init__(self):
        intents = discord.Intents.default()
        intents.members = True
        super().__init__(intents=intents)
        self.synced = False
        
    async def on_ready(self):
        await self.wait_until_ready()
        if not self.synced:
            await tree.sync()
            self.synced=True
        print(f'Logged in as {self.user}')
        
client = aclient()
tree = app_commands.CommandTree(client)

def next_available_row(worksheet,n):
                  str_list = list(filter(None, worksheet.col_values(n)))
                  return str(len(str_list)+1)

@tree.command(name='hi')
async def hi(interaction: discord.Interaction,user: discord.Member):
    await interaction.response.send_message(f"Hi {interaction.user.mention}!")
    # if interaction.user.id == 739375301578194944:
    #   await user.add_roles(interaction.guild.get_role(1005446174007885844))
      

def getDiscountFromAmount(amount):
  if amount >= 5 and amount <=14:
    return 5
  elif amount >= 15 and amount <= 29:
    return 15
  elif amount >= 30:
    return 30
  

def write_to_spreadsheet(name: str,id: int, address: str, balance: int):
    try:
        sa = gspread.service_account(filename='credentials.json')
        sh = sa.open("wild stag")
        worksheet = sh.worksheet("Sheet1")
        next_addy = next_available_row(worksheet=worksheet,n=3)
        next_name = next_available_row(worksheet=worksheet,n=1)
        next_id = next_available_row(worksheet=worksheet,n=2)
        amount = next_available_row(worksheet=worksheet,n=4)
        discount = next_available_row(worksheet=worksheet,n=5)
        worksheet.update_cell(next_addy,3,address)
        worksheet.update_cell(next_name,1,str(name))
        worksheet.update_cell(next_id,2,str(id))
        worksheet.update_cell(amount,4,str(balance))
        worksheet.update_cell(discount,5,str(getDiscountFromAmount(balance)))
        return True
    except Exception as e:
        print(f"{name} {e}")
        return False
    
def write_to_spreadsheetNFT(name: str,id: int, address: str, balance: int):
    try:
        sa = gspread.service_account(filename='credentials.json')
        sh = sa.open("wild stag")
        worksheet = sh.worksheet("Sheet2")
        next_addy = next_available_row(worksheet=worksheet,n=3)
        next_name = next_available_row(worksheet=worksheet,n=1)
        next_id = next_available_row(worksheet=worksheet,n=2)
        amount = next_available_row(worksheet=worksheet,n=4)
        discount = next_available_row(worksheet=worksheet,n=5)
        worksheet.update_cell(next_addy,3,address)
        worksheet.update_cell(next_name,1,str(name))
        worksheet.update_cell(next_id,2,str(id))
        worksheet.update_cell(amount,4,str(balance))
        worksheet.update_cell(discount,5,str(getDiscountFromAmount(balance)))
        return True
    except Exception as e:
        print(f"{name} {e}")
        return False

def return_ids_and_wallet_addresses():
    try:
        sa = gspread.service_account(filename='credentials.json')
        sh = sa.open("wild stag")
        worksheet = sh.worksheet("Sheet1")
        ids = worksheet.col_values(2)
        addresses = worksheet.col_values(3)
        ids.pop(0)
        addresses.pop(0)
        return ids, addresses
    except Exception as e:
        print(f"{e}")
        return [],[]
      
@tree.command(name='verify',description='Verify your wallet address')
async def myfunc(interaction: discord.Interaction):
  try:
      await interaction.response.defer(ephemeral=True)
      channel = interaction.channel
      guild = interaction.guild
      sdk = xumm.XummSdk('XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX','XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX')
      request ={
        "TransactionType": "SignIn"
      }
      def callback_func(event):
        if event['data']['signed'] == True:
          return event['data']
        if event['data']['signed'] == False:
            return False
      subscription = await sdk.payload.create_and_subscribe(
          request, 
          callback_func,
      )
      info = json.dumps(subscription.created.to_dict(), indent=4, sort_keys=True)
      d = json.loads(info)
      try:
        await interaction.followup.send(d['next']['always'],ephemeral=True)
        await interaction.channel.send(f"{interaction.user.mention} An xumm link has appeared, please sign it. After signing it, wait for 2 mins to get your role.")
        puuid = d['uuid']
      except Exception as e:
        dm1 = await interaction.user.create_dm()
        await dm1.send(d['next']['always'])
        await interaction.channel.send(f"{interaction.user.mention} An xumm link has appeared, please sign it. After signing it, wait for 2 mins to get your role.")
        puuid = d['uuid']
      try:
        dm = await interaction.user.create_dm()
      except discord.errors.Forbidden as e:
        await interaction.channel.send(f"{e}")
      await asyncio.sleep(120)
      result = sdk.payload.get(puuid)
      check = result.response.account
      if check != None:
            print(check)
            await interaction.channel.send(f"{interaction.user.mention} You have signed the request, you would be assigned your role shortly.")
            address = check
            async with AsyncWebsocketClient("wss://s1.ripple.com/") as websocket:
                account_lines_request = AccountLines(account=f"{address}",limit=400)
                nfts_req = AccountNFTs(account=f"{address}",limit=400)
                account_lines_response = await websocket.request(account_lines_request)
                nfts_response = await websocket.request(nfts_req)
                a=json.dumps(account_lines_response.to_dict(), indent=2)
                a1=json.loads(a)
                b1=nfts_response.result
                user = interaction.user
                nfts = 0
                print(len(a1['result']['lines']))
                balance = 0
                for x in b1['account_nfts']:
                    if x['Issuer'] == 'rLtgE7FjDfyJy5FGY87zoAuKtH6Bfb9QnE':
                      nfts += 1
                #have the same roles as the balances
                if   nfts == 0:
                  await channel.send(f"{interaction.user.mention} You Got the ***FAUN*** role!")
                  await user.add_roles(guild.get_role(985681328051728405))
                  write_to_spreadsheetNFT(name=user.name,id=user.id,address=address,balance=nfts)
                elif nfts >=1 and nfts < 3:
                  await channel.send(f"{interaction.user.mention} You Got the ***stag*** role!")
                  await user.add_roles(guild.get_role(985680840342261832))
                  write_to_spreadsheetNFT(name=user.name,id=user.id,address=address,balance=nfts)
                elif nfts >=3 and nfts < 5:
                  await channel.send(f"{interaction.user.mention} You Got the ***spiker*** role!")
                  await user.add_roles(guild.get_role(1028733097849663549))
                  write_to_spreadsheetNFT(name=user.name,id=user.id,address=address,balance=nfts)
                elif nfts >=5 and nfts < 15:
                  await channel.send(f"{interaction.user.mention} You Got the ***BROCKET*** role!")
                  await user.add_roles(guild.get_role(1028733335138205777))
                  write_to_spreadsheetNFT(name=user.name,id=user.id,address=address,balance=nfts)
                elif nfts >=15 and nfts < 30:
                  await channel.send(f"{interaction.user.mention} You Got the ***ROYAL*** role!")
                  await user.add_roles(guild.get_role(1028733495402573915))
                  write_to_spreadsheetNFT(name=user.name,id=user.id,address=address,balance=nfts)
                elif nfts >=30 and nfts < 100:
                  await channel.send(f"{interaction.user.mention} You Got the ***IMPERIAL*** role!")
                  await user.add_roles(guild.get_role(1028733620933906473))
                  write_to_spreadsheetNFT(name=user.name,id=user.id,address=address,balance=nfts)
                elif nfts >= 100:
                  await channel.send(f"{interaction.user.mention} You Got the ***MONARCH*** role!")
                  await user.add_roles(guild.get_role(1028733742493220965))
                  write_to_spreadsheetNFT(name=user.name,id=user.id,address=address,balance=nfts)
                else:
                  await channel.send(f"{interaction.user.mention} You don't have any nfts")
                for i in a1['result']['lines']:
                    if '5753544800000000000000000000000000000000' in i['currency']:
                        balance = float(i['balance'])
                        if  balance == 0:
                          await channel.send(f"{interaction.user.mention} You Got the ***FAUN*** role!")
                          await user.add_roles(guild.get_role(985681328051728405))
                          write_to_spreadsheet(name=user.name,id=user.id,address=address,balance=balance)
                        elif balance >=1 and balance < 3:
                          await channel.send(f"{interaction.user.mention} You Got the ***stag*** role!")
                          await user.add_roles(guild.get_role(985680840342261832))
                          write_to_spreadsheet(name=user.name,id=user.id,address=address,balance=balance)
                        elif balance >=3 and balance < 5:
                          await channel.send(f"{interaction.user.mention} You Got the ***spiker*** role!")
                          await user.add_roles(guild.get_role(1028733097849663549))
                          write_to_spreadsheet(name=user.name,id=user.id,address=address,balance=balance)
                        elif balance >=5 and balance < 15:
                          await channel.send(f"{interaction.user.mention} You Got the ***brocket*** role!")
                          await user.add_roles(guild.get_role(1028733335138205777))
                          write_to_spreadsheet(name=user.name,id=user.id,address=address,balance=balance)
                        elif balance >=15 and balance < 30:
                          await channel.send(f"{interaction.user.mention} You Got the ***ROYAL*** role!")
                          await user.add_roles(guild.get_role(1028733495402573915))
                          write_to_spreadsheet(name=user.name,id=user.id,address=address,balance=balance)
                        elif balance >=30 and balance < 100:
                          await channel.send(f"{interaction.user.mention} You Got the ***IMPERIAL*** role!")
                          await user.add_roles(guild.get_role(1028733620933906473))
                          write_to_spreadsheet(name=user.name,id=user.id,address=address,balance=balance)
                        elif balance >=100:
                          await channel.send(f"{interaction.user.mention} You Got the ***MONARCH*** role!")
                          await user.add_roles(guild.get_role(1028733742493220965))
                          write_to_spreadsheet(name=user.name,id=user.id,address=address,balance=balance)
                        break

  except Exception as e:
      await channel.send(f"{interaction.user.mention} An error has occurred, please try again later.")
      print(f"{interaction.user.name} has an error: {e}")
      return

@tree.command(name='verify-nft',description='verify nfts in your wallet')
async def myfunc2(interaction: discord.Interaction):
  try:
      await interaction.response.defer(ephemeral=True)
      channel = interaction.channel
      guild = interaction.guild
      sdk = xumm.XummSdk('XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX','XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX')
      request = {
        "TransactionType": "SignIn"
      }
      def callback_func(event):
        if event['data']['signed'] == True:
            return event['data']
        if event['data']['signed'] == False:
            return False
      subscription = await sdk.payload.create_and_subscribe(
            request,
            callback_func
        )
      await asyncio.sleep(1)
      info = json.dumps(subscription.created.to_dict(),
                      indent=4,sort_keys=True)
      d = json.loads(info)
      message = interaction.channel
      await asyncio.sleep(1)
      try:
        await interaction.followup.send(d['next']['always'],ephemeral=True)
        await interaction.channel.send(f"{interaction.user.mention} An xumm link has appeared, please sign it. After signing it, wait for 2 mins to get your role.")
        puuid = d['uuid']
      except Exception as e:
        dm1 = await interaction.user.create_dm()
        await dm1.send(d['next']['always'])
        await interaction.channel.send(f"{interaction.user.mention} An xumm link has appeared, please sign it. After signing it, wait for 2 mins to get your role.")
        puuid = d['uuid']
      try:
        dm = await interaction.user.create_dm()
      except discord.errors.Forbidden as e:
        await interaction.channel.send(f"{e}")
      await asyncio.sleep(100)
      result = sdk.payload.get(puuid)
      check = result.response.account
      if check != None:
        await message.send(f"Congrats {interaction.user.mention} you've successfully verified your role!")
        address = result.response.account
        user = interaction.user
        print('works4')
        tokenIds = []
        async with AsyncWebsocketClient("wss://s1.ripple.com/") as websocket:
            accountNftsRequest = AccountNFTs(account=f"{address}",limit=400)
            accountNftsResponse = await websocket.request(accountNftsRequest)
            for i in accountNftsResponse.result['account_nfts']:
              if i['Issuer'] == 'rLtgE7FjDfyJy5FGY87zoAuKtH6Bfb9QnE':
                tokenIds.append(i['NFTokenID'])
            nfts = len(tokenIds) #number of nfts
            if   nfts == 0:
              await channel.send(f"{interaction.user.mention} You Got the ***FAUN*** role!")
              await user.add_roles(guild.get_role(985681328051728405))
              write_to_spreadsheetNFT(name=user.name,id=user.id,address=address,balance=nfts)
            elif nfts >=1 and nfts < 3:
              await channel.send(f"{interaction.user.mention} You Got the ***STAG*** role!")
              await user.add_roles(guild.get_role(985680840342261832))
              write_to_spreadsheetNFT(name=user.name,id=user.id,address=address,balance=nfts)
            elif nfts >=3 and nfts < 5:
              await channel.send(f"{interaction.user.mention} You Got the ***SPIKER*** role!")
              await user.add_roles(guild.get_role(1028733097849663549))
              write_to_spreadsheetNFT(name=user.name,id=user.id,address=address,balance=nfts)
            elif nfts >=5 and nfts < 15:
              await channel.send(f"{interaction.user.mention} You Got the ***BROCKET*** role!")
              await user.add_roles(guild.get_role(1028733335138205777))
              write_to_spreadsheetNFT(name=user.name,id=user.id,address=address,balance=nfts)
            elif nfts >=15 and nfts < 30:
              await channel.send(f"{interaction.user.mention} You Got the ***ROYAL*** role!")
              await user.add_roles(guild.get_role(1028733495402573915))
              write_to_spreadsheetNFT(name=user.name,id=user.id,address=address,balance=nfts)
            elif nfts >=30 and nfts < 100:
              await channel.send(f"{interaction.user.mention} You Got the ***IMPERIAL*** role!")
              await user.add_roles(guild.get_role(1028733620933906473))
              write_to_spreadsheetNFT(name=user.name,id=user.id,address=address,balance=nfts)
            elif nfts >= 100:
              await channel.send(f"{interaction.user.mention} You Got the ***MONARCH*** role!")
              await user.add_roles(guild.get_role(1028733742493220965))
              write_to_spreadsheetNFT(name=user.name,id=user.id,address=address,balance=nfts)
            else:
              await channel.send(f"{interaction.user.mention} You don't have any nfts")
  except Exception as e:
    await interaction.channel.send(f"error: {e}")
      
@tree.command(name='check',description='updates all users roles')
@app_commands.checks.has_permissions(administrator=True)
async def check(interaction: discord.Interaction): 
  await interaction.response.defer(ephemeral=False)
  ids,address = return_ids_and_wallet_addresses()
  if len(ids) == 0:
    await interaction.channel.send(f"{interaction.user.mention} No users found in the spreadsheet.\nIf this problem persists, please contact the bot owner.")
    return
  await interaction.followup.send(f'Starting checks')
  counter = 0
  added = 0
  removed = 0
  for i in address:
    i = i.strip()
    async with AsyncWebsocketClient("wss://s1.ripple.com/") as websocket:
      account_lines_request = AccountLines(account=f"{i}",limit=400)
      account_lines_response = await websocket.request(account_lines_request)
      a = json.dumps(account_lines_response.to_dict(), indent=2)
      a1 = json.loads(a)
      print(ids[counter])
      try:
        user = interaction.guild.get_member(int(ids[counter]))
        #remove the roles from the user first
        try:
          await user.remove_roles(roles=[interaction.guild.get_role(985681328051728405),interaction.guild.get_role(985680840342261832),interaction.guild.get_role(1028733097849663549),interaction.guild.get_role(1028733335138205777),interaction.guild.get_role(1028733495402573915),interaction.guild.get_role(1028733620933906473),interaction.guild.get_role(1028733742493220965)])
        except:
          pass
        for j in a1['result']['lines']:
          if '5753544800000000000000000000000000000000' in j['currency']:
            balance = float(j['balance'])
            if balance >= 0 and balance < 1:
              await user.add_roles(interaction.guild.get_role(985681328051728405))
              added += 1
              break
            elif balance >=1 and balance < 3:
              await user.add_roles(interaction.guild.get_role(985680840342261832))
              added += 1
              break
            elif balance >=3 and balance < 5:
              await user.add_roles(interaction.guild.get_role(1028733097849663549))
              added += 1
              break
            elif balance >=5 and balance < 15:
              await user.add_roles(interaction.guild.get_role(1028733335138205777))
              added += 1
              break
            elif balance >=15 and balance < 30:
              await user.add_roles(interaction.guild.get_role(1028733495402573915))
              added += 1
              break
            elif balance >=30 and balance < 100:
              await user.add_roles(interaction.guild.get_role(1028733620933906473))
              added += 1
              break
            elif balance >=100:
              await user.add_roles(interaction.guild.get_role(1028733742493220965))
              added += 1
              break
            else:
              await user.remove_roles(interaction.guild.get_role(985681328051728405))
              await user.remove_roles(interaction.guild.get_role(985680840342261832))
              await user.remove_roles(interaction.guild.get_role(1028733097849663549))
              await user.remove_roles(interaction.guild.get_role(1028733335138205777))
              await user.remove_roles(interaction.guild.get_role(1028733495402573915))
              await user.remove_roles(interaction.guild.get_role(1028733620933906473))
              await user.remove_roles(interaction.guild.get_role(1028733742493220965))
              removed += 1
              break
          counter += 1
          await asyncio.sleep(1)
      except Exception as e:
        print(e)
        pass
      embed = discord.Embed(title="Check Complete", description=f"Added {added} roles", color=0x00ff00)
      await interaction.channel.send(embed=embed)

client.run('TOKENHERE')
      
