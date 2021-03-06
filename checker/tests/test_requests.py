from django.test import TestCase, Client
from django.urls import reverse
from rest_framework import status
import json
import base64
import os

client = Client()


class ExcelDataTest(TestCase):
    """ Test para los POST """

    def setUp(self):
        self.valid_file = ''
        with open(f"{os.getcwd()}/checker/tests/valid_excel.xlsx", "rb") as valid_file:
            self.valid_file = base64.b64encode(valid_file.read()).decode()
        self.valid_payload = {
            'name': 'Abowl',
            'date': '2022-10-22',
            'file': [self.valid_file],
        }

        self.invalid_missing_data_file = ''
        with open(f"{os.getcwd()}/checker/tests/invalid_excel.xlsx", "rb") as missing_data_file:
            self.invalid_missing_data_file = base64.b64encode(missing_data_file.read()).decode()

        self.invalid_missing_data_payload = {
            'name': 'Abowl',
            'date': '2022-10-22',
            'file': [self.invalid_missing_data_file],
        }

        self.invalid_file_type = ''
        with open(f"{os.getcwd()}/checker/tests/catpic.jpg", "rb") as invalid_file:
            self.invalid_file_type = base64.b64encode(invalid_file.read()).decode()

        self.invalid_file_type_payload = {
            'name': 'Abowl',
            'date': '2022-10-22',
            'file': [self.invalid_file_type],
        }

    def test_add_valid_data(self):
        response = client.post(
            reverse('save'),
            data=json.dumps(self.valid_payload),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_add_missing_data(self):
        response = client.post(
            reverse('save'),
            data=json.dumps(self.invalid_missing_data_payload),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_add_invalid_file(self):
        response = client.post(
            reverse('save'),
            data=json.dumps(self.invalid_file_type_payload),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
