import requests
import json
import re

from typing import Tuple, Union, Any
from time import sleep
from bs4 import BeautifulSoup
from discord_webhook import DiscordEmbed, DiscordWebhook

user_agent = {"user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.132 Safari/537.36"}

class DealabsMonitor:

    def __init__(self, group : str, webhook_url : str, sleep_delay : int) -> None:
        self.group = group
        self.webhook_url = webhook_url
        self.sleep_delay = sleep_delay
        self.__productsAlreadyPinged = []

    def __getProducts(self) -> list:
        list_products = []
        try:
            with requests.Session() as s:
                get = s.get(f"https://www.dealabs.com/groupe/{self.group}?page=1&ajax=true&layout=horizontal", headers=user_agent)
                if get.ok:
                    json_resp = json.loads(get.text)
                    soup = BeautifulSoup(json_resp["data"]["content"], features="html.parser")
                    products = soup.findAll("article")
                    for product in products:
                        if "thread--expired" not in product["class"]: # Check if the offer is expired
                            product_infos = product.findChild("a")
                            product_img = product.findChild("img")
                            product_price = product.findChild("span", {"class": re.compile(r"^thread-price")})
                            product_old_price = product.findChild("span", {"class": re.compile(r"^mute--text")})
                            product_to_ping = {
                                "name": product_infos["title"], 
                                "link_dealabs": product_infos["href"],
                                "link": "https://www.dealabs.com/visit/threadmain/" + product["id"][7:],
                                "price": product_price.text,
                                "old_price": None if not product_old_price else product_old_price.text,
                                "image": product_img["src"],
                                }
                            if product_to_ping not in self.__productsAlreadyPinged: # Check if the product has already been pinged
                                list_products.append(product_to_ping)
                else:
                    print("[Dealabs Monitor] Forbidden 1")       
        except Exception as e:
            print(f"[Dealabs Monitor] Unexpected error occured : {e}")
        finally:
            return list_products

    def __send_webhook(self, product : dict) -> Tuple[bool, Union[None, Any]]:
        embed = DiscordEmbed(title=product["name"], color="a0a0a0")
        embed.set_timestamp()
        embed.set_thumbnail(url=product["image"])
        if product["old_price"]:
            embed.add_embed_field(name="Price", value=f'**{product["price"]}** ~~{product["old_price"]}~~')
        else:
            embed.add_embed_field(name="Price", value=f'**{product["price"]}**')
        embed.add_embed_field(name="Direct Link", value=product["link"])
        embed.set_url(product["link_dealabs"])
        embed.set_footer(text="Dealabs Monitor")
        webhook = DiscordWebhook(url=self.webhook_url, username="Dealabs Monitor")
        webhook.add_embed(embed)
        try:
            resp = webhook.execute(remove_embeds=True, remove_files=True)
            if resp.ok:
                return True, None
            else:
                return False, f'[Dealabs Monitor] {resp}'
        except Exception as e:
            print(f'[Dealabs Monitor] : Error sending webhook ! {e}')
            return False, None

    def monitor(self) -> None:
        while True:
            products = self.__getProducts()
            for product in products:
                isSent, err = self.__send_webhook(product)
                if not isSent:
                    print(err)
                else:
                    self.__productsAlreadyPinged.append(product)
            sleep(self.sleep_delay)