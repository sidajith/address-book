import unittest
from elasticsearch import Elasticsearch
from flask import request
import addressbook

class TestCases(unittest.TestCase):
	def testHelpPost(self):
		addressbook.helpPost('Sid','8048733783','ajithsiddarth@gmail.com','1702 Gordon','UVA grad')
		addressbook.helpPost('Anne',None,None,'1702 Gordon','UVA grad')
		addressbook.helpPost('longPhoneNum','11111111111111111',None,'1702 Gordon','UVA grad')
		addressbook.helpPost('JustName',None,None,None,None)
		addressbook.helpPost('tooShortEmail',None,'no',None, None)
		self.assertTrue(es.exists(index='address-book', doc_type='contact', id='Sid'))
		#shows optional fields
		self.assertTrue(es.exists(index='address-book', doc_type='contact', id='Anne'))
		self.assertTrue(es.exists(index='address-book', doc_type='contact', id='JustName'))
		#false due to invalid number
		self.assertFalse(es.exists(index='address-book', doc_type='contact', id='longPhoneNum'))
		self.assertFalse(es.exists(index='address-book', doc_type='contact', id='tooShortEmail'))
		sid = es.get(index='address-book', doc_type='contact', id='Sid')["_source"]
		self.assertEqual(sid['phoneNumber'], '8048733783')
		self.assertEqual(sid['address'], '1702 Gordon')
		self.assertEqual(sid['bio'], 'UVA grad')

	def testGetNameFunc(self):
		addressbook.helpPost('Sid','8048733783','ajithsiddarth@gmail.com','1702 Gordon','UVA grad')
		self.assertEqual(addressbook.getNameFunc('Sid')[1] , 200)
		#error code for undeclared contact
		self.assertEqual(addressbook.getNameFunc('NowhereMan')[1] , 404)

	def testHelpPut(self):
		addressbook.helpPost('lossy', '86875309', None, None, None)
		#update values
		body = es.get(index='address-book', doc_type='contact', id='lossy')["_source"]
		body['phoneNumber']='12345867'
		body['address']='Not homeless'
		body['email']='realguy@yahoo.com'
		body['bio']='still boring'
		addressbook.helpPut('lossy',body)
		newBody = es.get(index='address-book', doc_type='contact', id='lossy')["_source"]
		self.assertEqual(newBody['phoneNumber'], '12345867')
		self.assertEqual(newBody['address'], 'Not homeless')
		self.assertEqual(newBody['bio'], 'still boring')
		body = newBody
		#show invalid inputs will not update the contact.
		body['phoneNumber']='12'
		addressbook.helpPut('lossy',body)
		newBody = es.get(index='address-book', doc_type='contact', id='lossy')["_source"]
		self.assertEqual(newBody['phoneNumber'], '12345867')


	def testDelFunc(self):
		addressbook.helpPost('tempFriend', None, None, None, None)
		self.assertTrue( es.exists(index='address-book', doc_type='contact', id='tempFriend'))
		addressbook.delFunc('tempFriend')
		self.assertTrue(not es.exists(index='address-book', doc_type='contact', id='tempFriend'))

if __name__ == '__main__':
	es = Elasticsearch()
	es.indices.delete(index='address-book', ignore=[400, 404])
	es.indices.create(index='address-book', ignore=[400, 404])
	unittest.main()
