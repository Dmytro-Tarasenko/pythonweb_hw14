import unittest
from src.contacts import routes
# from src.contacts.orms import ContactORM
# from src.db import get_db
from src.contacts.models import Contact, ContactResponse


class TestContactCase(unittest.TestCase):
    def test_get_field_names(self):
        fields = routes.get_field_names(Contact)
        reference = ['first_name', 'last_name', 'phone', 'email', 'birthday', 'extra', 'full_name']
        self.assertEqual(fields.sort(), reference.sort())

    def test_add_contact_success(self):
        contact = Contact(first_name='John',
                          last_name='Doe',
                          phone='1234567890',
                          email='asdasd@asdasd.net')




if __name__ == '__main__':
    unittest.main()
