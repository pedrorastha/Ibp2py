import unittest
from unittest.mock import patch, MagicMock, ANY
from ibpy import ibpy  # Import your ibpy class
import xml.etree.ElementTree as ET
import pandas as pd

class TestIbpy(unittest.TestCase):
    def setUp(self):
        self.ibpy_instance = ibpy('username', 'password', 'host')

    @patch('requests.get')
    def test_get_data(self, mock_get):
        mock_get.return_value.content = '<xml>Some data</xml>'
        result = self.ibpy_instance._ibpy__get_data('entity_set', {})
        mock_get.assert_called_once()
        self.assertEqual(result, '<xml>Some data</xml>')

    @patch('xml.etree.ElementTree.fromstring')
    @patch('pandas.DataFrame')
    def test_process_response(self, mock_df, mock_xml_element):
        mock_element = ET.Element('test')
        mock_xml_element.return_value = mock_element
        mock_df.return_value = pd.DataFrame()  # Return a real DataFrame
        result = self.ibpy_instance._ibpy__process_response('<xml>Some data</xml>')
        mock_element.findall.assert_called_once_with('atom:entry', ANY)
        mock_df.assert_called_once_with([])

    @patch('requests.get')
    def test_masterdata(self, mock_get):
        mock_get.return_value.content = '<xml>Some data</xml>'
        result = self.ibpy_instance.masterdata('MasterData', 'select')
        mock_get.assert_called_once()

    @patch('requests.get')
    def test_keyfigure(self, mock_get):
        mock_get.return_value.content = '<xml>Some data</xml>'
        result = self.ibpy_instance.keyfigure('PlanningAreaID', 'MasterData', 'KeyFigures')
        mock_get.assert_called_once()

    @patch('requests.get')
    def test_telemetry(self, mock_get):
        mock_get.return_value.content = '<xml>Some data</xml>'
        result = self.ibpy_instance.telemetry('PlanningView')
        mock_get.assert_called_once()

if __name__ == '__main__':
    unittest.main()
