from netmiko import ConnectHandler
import time
import concurrent.futures
import datetime
import re

ip_address_file = input('Enter name of file for host addresses: ').strip()
t1 = time.perf_counter()

def fetch_ip_addresses():
   with open(ip_address_file) as devices:
       addresses = devices.read().splitlines()
   return addresses

def backgup_file(filename, output):    
   with open(filename.group(0),'w') as backup_file:
       backup_file.write(output)
       print('Configurations were successfully backed up!')
   return

def backup_rtr_configuration(address):
   todays_date = datetime.datetime.now()
   year = todays_date.year
   day = todays_date.day
   month = todays_date.month

   ios_device_info = {
       'ip': address,
       'port': 22,
       'username': 'u28057',
       'password': 'ATLfal2#',
       'device_type': 'cisco_ios',
       'verbose': True
   }
   #There are two types of classifications for commands: 1) show commands 2) configuring commands(anything that will add, delete, alter).
   #Always test configuring commands on lab devices first before going into production.
   #This command below in line 38 is used to configure something on the devices so make sure to test these on a lab devices first.
   #command = ["username Batmanadmin privilege 15 password Batmanadmin!234"]
   print(f'Connecting to host {address}...')
   ssh_connection = ConnectHandler(**ios_device_info)

   print(f'Generating running configuration for host {address}...')
   #This below in line 44 is the code format used for configuring a device
   #output = ssh_connection.send_config_set(command)
   #example of show command code format will be here below in line 46; to test it, uncomment line 46 and add # to begin lines 38 and 44.
   output = ssh_connection.send_command('show ip int brief')
   prompt_hostname = ssh_connection.find_prompt()[0:-1]
   filename = f'{prompt_hostname}_{month}_{day}_{year}_backgup.cfg'
   print(output)

   print(f'Backing up configuration for host {address}')
   time.sleep(1)
   backgup_file(filename, output)
   ssh_connection.disconnect()
   return
#This method below is used for multithreading so multiple devices can be configured with minnimum time.
with concurrent.futures.ThreadPoolExecutor() as exe:
   ip_addresses = fetch_ip_addresses()
   results = exe.map(backup_rtr_configuration, ip_addresses)

t2 = time.perf_counter()
print(f'The script finished executing in {round(t2-t1,2)} seconds.')
