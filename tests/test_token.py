# -*- coding: utf-8 -*-

from unittest import TestCase
from bnfparsing.token import Token

class TokenTestSuite(TestCase):

    def test_token_creation(self):
        string = 'TEST'
        token = Token(token_type=string, text=string)
        self.assertEqual(token.token_type, string)
        self.assertEqual(token.text, string)

    def test_children(self):
        num = 5
        master = Token()
        self.assertFalse(master)
        for index in range(num):
            master.add(Token(text=str(index)))
        self.assertTrue(master)
        self.assertEqual(master[0].text, '0')
        self.assertEqual(len(master), num)
        counter = 0
        for child in master:
            self.assertEqual(child.text, str(counter))
            counter += 1
        self.assertEqual(counter, num)
