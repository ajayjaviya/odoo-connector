# -*- coding: utf-8 -*-
from odoo.tests.common import SavepointCase


class MagentoInstanceTest(SavepointCase):
    """ Base class - Test the Import Magento store.
    """

    def setUp(self):
        super(MagentoInstanceTest, self).setUp()
        self.instance_model = self.env['magento.instance']
        self.instance = self.instance_model.create(
            {'name': 'Test Magento',
             'location': 'http://m2.com',
             'access_token': 'n1axpdbd8jf4ctyx9q0x9y3v6t3e0ngi',
             }
        )
