#Назначение программы: извлечение структурированной информации с веб-сайтов
import os
from urllib.request import urlopen
import pip
import selenium
from requests.exceptions import HTTPError
import yaml
from pip._vendor import requests
from selenium.webdriver.common.by import By
from selenium import webdriver
import re
from bs4 import BeautifulSoup
from zodbpickle import pickle
import ZODB
from ZODB import FileStorage, DB
import transaction

#путь к драйверу
app_path = 'geckodriver-v0.29.0-linux64/'

os.environ["PATH"] += os.pathsep + app_path


class Device():
    def __init__(self, device_model='', released_date='', device_vendor='', device_name='', device_type='',
                 device_codename='', device_dimensions_height='', device_dimensions_width='',
                 device_dimensions_depth='', device_display_type='', device_display_resolution='', device_soc='',
                 device_cpu='', device_gpu='', device_ram='', device_internal_card_type='',
                 device_internal_card_size='', device_peripherals_sim='', device_peripherals_bluetooth='',
                 device_peripherals_wifi='', device_peripherals_usb='', device_peripherals_nfc='',
                 device_peripherals_gps='', device_peripherals_sensors='', device_number_of_cameras='',
                 device_parametres_of_cameras='', device_battery_removable='', device_battery_type='',
                 device_battery_capacity=''):
        self.device_model = device_model
        self.released_date = released_date
        self.device_vendor = device_vendor
        self.device_name = device_name
        self.device_type = device_type
        self.device_codename = device_codename
        self.device_dimensions_height = device_dimensions_height
        self.device_dimensions_width = device_dimensions_width
        self.device_dimensions_depth = device_dimensions_depth
        self.device_display_type = device_display_type
        self.device_display_resolution = device_display_resolution
        self.device_soc = device_soc
        self.device_cpu = device_cpu
        self.device_gpu = device_gpu
        self.device_ram = device_ram
        self.device_internal_card_type = device_internal_card_type
        self.device_internal_card_size = device_internal_card_size
        self.device_peripherals_sim = device_peripherals_sim
        self.device_peripherals_bluetooth = device_peripherals_bluetooth
        self.device_peripherals_wifi = device_peripherals_wifi
        self.device_peripherals_usb = device_peripherals_usb
        self.device_peripherals_nfc = device_peripherals_nfc
        self.device_peripherals_gps = device_peripherals_gps
        self.device_peripherals_sensors = device_peripherals_sensors
        self.device_number_of_cameras = device_number_of_cameras
        self.device_parametres_of_cameras = device_parametres_of_cameras
        self.device_battery_removable = device_battery_removable
        self.device_battery_type = device_battery_type
        self.device_battery_capacity = device_battery_capacity

    def add_rom(self, project, page, download_link):
        pass

    def add_recovery(self, page, download_link):
        pass


class Project():
    def __init__(self, kwargs, stdmobile_device):
        self.params = {}
        self.stdmobile_device = stdmobile_device
        for key in kwargs:
            self.params[key] = kwargs[key]
            print("key = {0}, value = {1}".format(key, kwargs[key]))
    #поиск моделей устройств
    def get_structure_model(self, device_param):
      try:
            response = requests.get(self.params['device_page'])
            response.raise_for_status()
            # обработка исключений 403, 404 и т.д.
      except HTTPError as http_err:
            print(f'HTTP error occurred: {http_err}')
      except Exception as err:
            print(f'Other error occurred: {err}')
      else:
        driver = webdriver.Chrome()
        driver.get(self.params['device_page'])
        element = driver.find_element_by_partial_link_text(device_param)
        parents_path = []
        new_path = '..'
        parent = element.find_element_by_xpath(new_path)
        while (parent.tag_name != 'body'):
            parents_path.append(parent.tag_name)
            new_path += '/..'
            parent = element.find_element_by_xpath(new_path)

        xpath = '/'
        for e in parents_path[::-1]:
            xpath += "/" + e
        xpath += "/" + element.tag_name
       # print('FIND PATH', xpath)
        result = driver.find_elements(By.XPATH, xpath)
       # print(driver.find_elements(By.XPATH, xpath))
        models = []
        for i in result:
            models.append(i.text)
        #print(models)
        storage = FileStorage.FileStorage('models.fs')    #создаем файл models.fs
        db = DB(storage)
        connection = db.open()                  #открываем БД
        root = connection.root()               # Объект подключения позволяет получить доступ к корневому контейнеру с помощью вызова метода root()
        root['models'] = models
        transaction.commit()                    #сохранениe изменений в БД
        connection.close()                     #закроем соединение
        print(root.items())  # проверяем, что сохранилось в БД

    def get_structure_parametres(self, device_param):

       try:
            response = requests.get(self.params['device_page'])
            response.raise_for_status()
            # обработка исключений 403, 404 и т.д.
       except HTTPError as http_err:
            print(f'HTTP error occurred: {http_err}')
       except Exception as err:
            print(f'Other error occurred: {err}')

       else:
              # подключаем драйвер
         driver = webdriver.Chrome()
              # в качестве параметра передаем веб-страницу проекта
         driver.get(self.params['device_page'])
             #находим элемент по параметру устройства (device_param)
         try:
             element = driver.find_element_by_partial_link_text(device_param)
         except  selenium.common.exceptions.NoSuchElementException:
             print(f'HTTP error occurred: 404')
         else:
          parents_path = []
          new_path = '..'
          #находим элемент по XPath
          parent = element.find_element_by_xpath(new_path)
             #находим XPath до тега 'body'
          while (parent.tag_name != 'body'):
                parents_path.append(parent.tag_name)
                new_path += '/..'
                parent = element.find_element_by_xpath(new_path)
          xpath = '/'
          for e in parents_path[::-1]:
                xpath += "/" + e
          xpath += "/" + element.tag_name
         #   print('FIND PATH', xpath)
             #находим остальные устройства по XPath
          result = driver.find_elements(By.XPATH, xpath)
          codenames = []
          for i in result:
                  codenames.append(i.text)
         #   print(driver.find_elements(By.XPATH, xpath))
             #массив, в котором будет содержаться контент страниц устройств
          content_of_pages=[]
        # print(codenames)
          for i in result:
                content_of_pages.append(i.text)
           # print(content_of_pages)
             #массив, в котором содержатся все ссылки на устройства
          links=[]
          names=[]
          years=[]
          soc = []
          ram=[]
          cpu=[]
          Architecture=[]
          gpu=[]
          network=[]
          sd=[]
          screen=[]
          wifi=[]
          bluetooth=[]
          peripherals=[]
          camera=[]
          battery=[]
          k=0
          for i in result:
                links.append(i.get_attribute("href"))
                k=k+1
          print(k)
          storage = FileStorage.FileStorage('parametres_of_device.fs')  # создаем файл parametres_of_device.fs
          db = DB(storage)
          connection = db.open()  # открываем БД
          root = connection.root()  # Объект подключения позволяет получить доступ к корневому контейнеру с помощью вызова метода root()
             #находим информацию о каждом устройстве
          for j in links:
              URL = j
              session = requests.Session()
              try:
                  request = session.get(URL)
              except pip._vendor.requests.exceptions.InvalidSchema:
                    print('No connection adapters')
              else:
                soup = BeautifulSoup(request.text, 'html.parser')
                c = soup.text
                #записываем всю информацию об устройстве в 1 строку
                content = c.split()
                content1 = ' '.join(content)
                #print(content1)
                year_of_release=re.search('[20]\d{3}', content1)
                if result:
                    years.append(year_of_release.group(0))

                if (content1.find('SoC')!=-1):
                    index_SoC = c.find('SoC')
                    index_RAM = c.find('RAM')
                    soc1 = c[index_SoC+3:index_RAM]
                    soc1 = " ".join(soc1.split())
                    soc.append(soc1)
                if (content1.find('RAM')!=-1):
                    index_RAM = c.find('RAM')
                    index_CPU = c.find('CPU')
                    ram1 = c[index_RAM+3:index_CPU]
                    ram1 = " ".join(ram1.split())
                    ram.append(ram1)
                if (content1.find('CPU')!=-1):
                    index_CPU = c.find('CPU')
                    index_architecture = c.find('Architecture')
                    cpu1 = c[index_CPU+3:index_architecture]
                    cpu1 = " ".join(cpu1.split())
                    cpu.append(cpu1)
                if (content1.find('Architecture')!=-1):
                    index_architecture = c.find('Architecture')
                    index_GPU = c.find('GPU')
                    Architecture1 = c[index_architecture+12:index_GPU]
                    Architecture1 = " ".join(Architecture1.split())
                    Architecture.append(Architecture1)
                if (content1.find('GPU')!=-1):
                    index_GPU = c.find('GPU')
                    index_Network = c.find('Network')
                    gpu1 = c[index_GPU+3:index_Network]
                    gpu1 = " ".join(gpu1.split())
                    gpu.append(gpu1)
                if (content1.find('Network')!=-1):
                    index_Network = c.find('Network')
                    index_Storage = c.find('Storage')
                    network1 = c[index_Network+7:index_Storage]
                    network1 = " ".join(network1.split())
                    network.append(network1)

                if (content1.find('SD card')!=-1):
                    index_SD = c.find('SD card')
                    index_Screen = c.find('Screen')
                    sd1 = c[index_SD+7:index_Screen]
                    sd1 = " ".join(sd1.split())
                    sd.append(sd1)
                if (content1.find('Screen')!=-1):
                    index_Screen = c.find('Screen')
                    index_colors = c.find('colors')
                    screen1 = c[index_Screen+7:index_colors+6]
                    screen1 = " ".join(screen1.split())
                    screen.append(screen1)
                if (content1.find('Bluetooth')!=-1):
                    index_bluetooth = c.find('Bluetooth')
                    index_wifi = c.find('Wi-Fi')
                    bluetooth1 = c[index_bluetooth+9:index_wifi]
                    bluetooth1 = " ".join(bluetooth1.split())
                    bluetooth.append(bluetooth1)
                if (content1.find('Wi-Fi')!=-1):
                    index_wifi = c.find('Wi-Fi')
                    index_peripherals = c.find('Peripherals')
                    wifi1 = c[index_wifi+5:index_peripherals]
                    wifi1 = " ".join(wifi1.split())
                    wifi.append(wifi1)
                if (content1.find('Peripherals')!=-1):
                    index_peripherals = c.find('Peripherals')
                    index_camera = c.find('Camera')
                    peripherals1 = c[index_peripherals+11:index_camera]
                    peripherals1 = " ".join(peripherals1.split())
                    peripherals.append(peripherals1)
                if (content1.find('flash')!=-1):
                    index_camera = c.find('Camera')
                    index_flash = c.find('flash')
                    camera1 = c[index_camera+9:index_flash]
                    camera1 = " ".join(camera1.split())
                    camera.append(camera1)
                if (content1.find('Battery')!=-1):
                    index_battery = c.find('Battery')
                    index_mAh = c.find('mAh')
                    battery1 = c[index_battery+7:index_mAh+3]
                    battery1 = " ".join(battery1.split())
                    battery.append(battery1)
          root['year'] = years
          root['SoC'] = soc
          root['RAM']=ram
          root['CPU']=cpu
          root['Architecture']=Architecture
          root['GPU']=gpu
          root['Screen']=screen
          root['Bluetooth']=bluetooth
          root['Wi-Fi']=wifi
          root['Peripherals']=peripherals
          root['Cameras']=camera
          root['Battery']=battery
          root['Codenames']=codenames
          transaction.commit()  # сохранениe изменений в БД
          connection.close()  # закроем соединение
          print(root.items())  # проверяем, что сохранилось в БД
   #парсер для twrp
    def get_structure_model_twrp(self, device_param):
      try:
            response = requests.get(self.params['device_page'])
            response.raise_for_status()
            # обработка исключений 403, 404 и т.д.
      except HTTPError as http_err:
            print(f'HTTP error occurred: {http_err}')
      except Exception as err:
            print(f'Other error occurred: {err}')
      else:
        # подключаем драйвер
        driver = webdriver.Chrome()
        # в качестве параметра передаем веб-страницу проекта
        driver.get(self.params['device_page'])
        # находим элемент по параметру устройства (device_param)
        element = driver.find_element_by_partial_link_text(device_param)
        parents_path = []
        new_path = '..'
        # находим элемент по XPath
        parent = element.find_element_by_xpath(new_path)
        # находим XPath до тега 'body'
        while (parent.tag_name != 'body'):
            parents_path.append(parent.tag_name)
            new_path += '/..'
            parent = element.find_element_by_xpath(new_path)

        xpath = '/'
        for e in parents_path[::-1]:
            xpath += "/" + e
        xpath += "/" + element.tag_name
        print('FIND PATH', xpath)
        # находим остальные устройства по XPath
        result = driver.find_elements(By.XPATH, xpath)
        #print(driver.find_elements(By.XPATH, xpath))
        # массив, в котором содержатся все ссылки на производителей устройств
        links = []
        # список моделей устройств одного производителя
        models1=[]

        for i in result:
            links.append(i.get_attribute("href"))
       # print(links)
        # находим информацию о каждом устройстве
          #считываем все ссылки на устройства
        for j in links:
            session = requests.Session()
            request = session.get(j)
            soup = BeautifulSoup(request.text, 'html.parser')
            links_of_devices = []
            #ссылки на каждое устройство
            links2=[]
            #список моделей устройств одного производителя
            models=[]

            links_of_devices=soup.find_all("strong")
        #    print(links_of_devices)
            for link in links_of_devices:
                links2.append(link.find("a").get("href"))
                models.append((link.find("a").text))
            models1.extend(models)   #добавить список моделей одного производителя к списку моделей всех производителей
        print(models1)

      storage = FileStorage.FileStorage('models.fs')  # создаем файл models.fs
      db = DB(storage)
      connection = db.open()  # открываем БД
      root = connection.root()  # Объект подключения позволяет получить доступ к корневому контейнеру с помощью вызова метода root()
      root['models'] = models1
      transaction.commit()  # сохранениe изменений в БД
      connection.close()  # закроем соединение
      print(root.items())  # проверяем, что сохранилось в БД

    def get_structure_parametres_twrp(self, device_param):
      try:
            response = requests.get(self.params['device_page'])
            response.raise_for_status()
            # обработка исключений 403, 404 и т.д.
      except HTTPError as http_err:
            print(f'HTTP error occurred: {http_err}')
      except Exception as err:
            print(f'Other error occurred: {err}')
      else:
        # подключаем драйвер
        driver = webdriver.Chrome()
        # в качестве параметра передаем веб-страницу проекта
        driver.get(self.params['device_page'])
        # находим элемент по параметру устройства (device_param)
        element = driver.find_element_by_partial_link_text(device_param)

        parents_path = []
        new_path = '..'
        # находим элемент по XPath
        parent = element.find_element_by_xpath(new_path)
        # находим XPath до тега 'body'
        while (parent.tag_name != 'body'):
            parents_path.append(parent.tag_name)
            new_path += '/..'
            parent = element.find_element_by_xpath(new_path)

        xpath = '/'
        for e in parents_path[::-1]:
            xpath += "/" + e
        xpath += "/" + element.tag_name
        print('FIND PATH', xpath)
        # находим остальные устройства по XPath
        result = driver.find_elements(By.XPATH, xpath)
        #print(driver.find_elements(By.XPATH, xpath))
        # массив, в котором содержатся все ссылки на производителей устройств
        links = []
        # список моделей устройств одного производителя
        models1=[]

        for i in result:
            links.append(i.get_attribute("href"))
       # print(links)
        # находим информацию о каждом устройстве
          #считываем все ссылки на устройства
        for j in links:
            session = requests.Session()
            request = session.get(j)
            soup = BeautifulSoup(request.text, 'html.parser')
            links_of_devices = []
            #ссылки на каждое устройство
            links2=[]
            #список моделей устройств одного производителя
            models=[]

            links_of_devices=soup.find_all("strong")
        #    print(links_of_devices)
            for link in links_of_devices:
                links2.append(link.find("a").get("href"))
                models.append((link.find("a").text))
            models1.extend(models)   #добавить список моделей одного производителя к списку моделей всех производителей
     #   print(models1)
     #   for model in models:
        #   print(model)
          #  for i in links2:
           #     URL="https://twrp.me"+i
            #    session = requests.Session()
            #    request = session.get(URL)
           #     soup = BeautifulSoup(request.text, 'html.parser')
           #     c = soup.text
          #      # записываем всю информацию об устройстве в 1 строку
           #     content = c.split()
         #       print(content)
      storage = FileStorage.FileStorage('parametres_of_device.fs')  # создаем файл models.fs
      db = DB(storage)
      connection = db.open()  # открываем БД
      root = connection.root()  # Объект подключения позволяет получить доступ к корневому контейнеру с помощью вызова метода root()
      root['names (codenames)'] = models1
      transaction.commit()  # сохранениe изменений в БД
      connection.close()  # закроем соединение
      print(root.items())  # проверяем, что сохранилось в БД

class StdMobileDevice():
    def __init__(self, kwargs):
        self.params = {}
        for key in kwargs:
            self.params[key] = kwargs[key]
            #print("key = {0}, value = {1}".format(key, kwargs[key]))


projects = {}
with open('config.yml', 'r') as f:
    config = yaml.safe_load(f)
    standard_dev = StdMobileDevice(config['standard_device'])
    for prj in config['sites']:
        projects[prj['name']] = Project(prj, standard_dev)
    for prj in config['recovery']:
        projects[prj['name']] = Project(prj, standard_dev)

#projects['e.foundation'].get_structure_model(projects['e.foundation'].stdmobile_device.params['device_model'])
#projects['LineageOS'].get_structure_model(projects['LineageOS'].stdmobile_device.params['device_name'])
#projects['crDroid'].get_structure_model(projects['crDroid'].stdmobile_device.params['device_model'])
#projects['Resurrection Remix OS'].get_structure_model(projects['Resurrection Remix OS'].stdmobile_device.params['device_model'])
#projects['AospExtended ROM'].get_structure_model(projects['AospExtended ROM'].stdmobile_device.params['device_model'])
#projects['twrp'].get_structure_model_twrp(projects['twrp'].stdmobile_device.params['device_vendor'])
#projects['crDroid'].get_structure_parametres(projects['crDroid'].stdmobile_device.params['device_model'])
#projects['e.foundation'].get_structure_parametres(projects['e.foundation'].stdmobile_device.params['device_name'])
#projects['LineageOS'].get_structure_parametres(projects['LineageOS'].stdmobile_device.params['device_model'])
#projects['Resurrection Remix OS'].get_structure_parametres(projects['Resurrection Remix OS'].stdmobile_device.params['device_model'])
#projects['AospExtended ROM'].get_structure_parametres(projects['AospExtended ROM'].stdmobile_device.params['device_model'])
#projects['twrp'].get_structure_parametres_twrp(projects['twrp'].stdmobile_device.params['device_vendor'])
