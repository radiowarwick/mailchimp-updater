import configparser
import xml.etree.ElementTree as ET
import urllib.request as request
from mailchimp3 import MailChimp

config = configparser.ConfigParser()
config.read('mailchimp.config')

mailchimp_api_key = config['mailchimp']['api_key']
mailchimp_api_user = config['mailchimp']['api_user']
mailchimp_list_id = config['mailchimp']['list_id']
su_api_key = config['su']['api_key']

su_url = 'https://www.warwicksu.com/membershipapi/listmembers/' + su_api_key + '/'
members_xml = request.urlopen(su_url).read()
root = ET.fromstring(members_xml)

members = {}
for member in root:
	info = {}
	for part in member:
		info[part.tag] = part.text
	members[info['UniqueID']] = info

mc = MailChimp(mc_api=mailchimp_api_key, mc_user=mailchimp_api_user)
list_members = mc.lists.members.all(mailchimp_list_id, get_all=True, fields='members.email_address,members.merge_fields')

for id, data in members.items():
	found = False
	for list_member in list_members['members']:
		if list_member['email_address'] == data['EmailAddress']:
			found = True
			break

	if not found:
		print('Added the following to the mailing list', data, sep='\n')
		try:
			mc.lists.members.create(mailchimp_list_id, {
				'email_address': data['EmailAddress'],
				'status': 'subscribed',
				'merge_fields': {
					'FNAME': data['FirstName'],
					'LNAME': data['LastName']
				}
			})
		except Exception as e:
			print(e)