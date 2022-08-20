from dhooks import Webhook, Embed
import discord
import requests
import json
import bs4
import time
from colorama import Fore, Back, Style

email = 'INSERT EMAIL'
password = 'INSERT PASSWORD'
discordWebhook = "INSERT DISCORD WEBHOOK"

headers = {
    'authority': 'restocks.net',
    'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
    'accept-language': 'it-IT,it;q=0.9',
    'cache-control': 'max-age=0',
    'origin': 'https://restocks.net',
    'referer': 'https://restocks.net/it/login',
    'sec-ch-ua': '"Chromium";v="104", " Not A;Brand";v="99", "Google Chrome";v="104"',
    'sec-ch-ua-mobile': '?0',
    'sec-ch-ua-platform': '"Windows"',
    'sec-fetch-dest': 'document',
    'sec-fetch-mode': 'navigate',
    'sec-fetch-site': 'same-origin',
    'sec-fetch-user': '?1',
    'upgrade-insecure-requests': '1',
}

session = requests.Session()

r = session.get('https://restocks.net/it/login', headers=headers)
print(Fore.YELLOW + "Getting csrf token..."+Fore.RESET)
soup = bs4.BeautifulSoup(r.text, 'html.parser')
csrf_token = soup.find('meta', {'name': 'csrf-token'})['content']
data = {
    '_token': str(csrf_token),
    'email': email,
    'password': password,
}
print(Fore.YELLOW + "Logging in..."+Fore.RESET)
r = session.post('https://restocks.net/it/login', headers=headers, data=data)
while True:
    print(Fore.YELLOW + "Getting products on sale..."+Fore.RESET)
    r = session.get('https://restocks.net/it/account/listings/resale?page=1&search=', headers=headers)
    data = json.loads(r.text)
    products_inventory = data["products"]
    soup = bs4.BeautifulSoup(products_inventory, 'html.parser')
    items = soup.find_all('tr', {'class': 'clickable'})
    for item in items:
        img = item.find('img')['src']
        id = item.find('input',{'class':'productid'})['value']
        price = item.find('input', {'class': 'price'})['value']
        name = item.find('span').text
        baseid = item.find('input', {'class': 'baseproductid'})['value']
        sizeid = item.find('input', {'class': 'sizeid'})['value']

        if '<span class="storeprice red">' in str(item):
            r = session.get('https://restocks.net/it/product/get-lowest-price/'+str(baseid)+'/'+str(sizeid)+'/'+str(id), headers=headers)
            newprice = r.text
            print(Fore.GREEN + "New Price of "+str(newprice)+" for "+str(name)+ Fore.RESET)

            newprice_edit = int(newprice) - 1

            r = session.get('https://restocks.net/it/account/listings', headers = headers)
            soup = bs4.BeautifulSoup(r.text, 'html.parser')
            csrf_token = soup.find('meta', {'name': 'csrf-token'})['content']
            data = {
                '_token': csrf_token,
                'id': str(id),
                'store_price': str(newprice_edit)
            }
            r = session.post('https://restocks.net/it/account/listings/edit', headers = headers, data = data)
            if '"success":true' in r.text:
                print(Fore.GREEN + "Price updated ["+str(newprice_edit)+"] for item "+str(name) + Fore.RESET)
                embed = Embed(
                        color = 0xf7c328,
                        description = None,
                        timestamp= 'now'
                    )

                embed.set_title(title= 'RESTOCKS UNDERCUTTER', url = 'https://restocks.net/it/account/listings')
                embed.add_field(name = 'Item', value = name,inline = False)
                embed.add_field(name = 'Listing ID', value = str(id))
                embed.add_field(name = 'Old Price', value = str(price))
                embed.add_field(name = 'New Price', value = str(newprice_edit))
                embed.set_footer(text= 'made by @WashedDragonyx', icon_url='https://pbs.twimg.com/profile_images/1387046154186084355/9B34r5d2_400x400.jpg')
                embed.set_thumbnail(img)
                hook = Webhook(discordWebhook)
                hook.send(embed=embed)
            else:
                print(r.text)
        else:
            print(Fore.YELLOW + "No price update for item "+str(name) + Fore.RESET)
    
    time.sleep(30)

           

    