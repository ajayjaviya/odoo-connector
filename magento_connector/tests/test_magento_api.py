# -*- coding: utf-8 -*-
from .common import MagentoInstanceTest


class TestMagentoAPI(MagentoInstanceTest):
    def test_magento_api(self):
        """ Test the Magento API
            - For test here call import store url
            - If successfull magento sent response with status code 200
        """
        url = '/rest/V1/store/storeViews'
        response = self.instance.magento_api(url)
        self.assertEqual(response.status_code, 200,
                         'Magento: Something goes wrong Magento API is not incorrect.')
