import requests
from requests.auth import HTTPBasicAuth
import xmltodict
import json
import pandas as pd



class LOG_VIEW_SRV:

    def __init__(self, username, password):
        self.username = username
        self.password = password
        self.base_url = 'https://my301284-api.scmibp1.ondemand.com/sap/opu/odata/IBP/LOG_VIEW_SRV'

    def _get_headers(self):
        self.csrf_token = self._get_CSRF_token()
        headers = {
            "X-CSRF-Token": self.csrf_token,
            'config_authType': 'Basic',
            'config_packageName': 'IBPAPIMonitoringIntegrationService',
            'config_actualUrl': 'https://my301284-api.scmibp1.ondemand.com/sap/opu/odata/IBP/LOG_VIEW_SRV',
            'config_urlPattern': 'https://{host}/sap/opu/odata/IBP/{servicePath}',
            'config_apiName': 'IBP_Log_Views_ODataService',
            "DataServiceVersion": "2.0",
            "Accept": "*/*"
        }
        return headers    

    def _get_CSRF_token(self):
        url = f'{self.base_url}/$metadata'

        headers = {
            "X-CSRF-Token": "fetch",
            'config_authType': 'Basic',
            'config_packageName': 'IBPAPIMonitoringIntegrationService',
            'config_actualUrl': 'https://my301284-api.scmibp1.ondemand.com/sap/opu/odata/IBP/LOG_VIEW_SRV',
            'config_urlPattern': 'https://{host}/sap/opu/odata/IBP/{servicePath}',
            'config_apiName': 'IBP_Log_Views_ODataService',
            'DataServiceVersion': '2.0',
            'Accept': '*/*'
        }

        response = requests.get(url, headers=headers, auth=HTTPBasicAuth(self.username, self.password))
        if response.status_code == 200:
            return 'fetch'#response.headers.get('X-CSRF-Token')
        else:
            return None


    def _get_entity_data(self, entity_set_name, query_params=None):
        headers = self._get_headers()
        url = f'{self.base_url}{entity_set_name}'
        response = requests.get(url, headers=headers, params=query_params, auth=HTTPBasicAuth(self.username, self.password))
        if response.status_code != 200:
            raise Exception(f"Failed to get data from {entity_set_name}. Status code: {response.status_code}")
        return response  # or some other format


    def _convert_xml_to_dataframe(self, xml_response):
        def extract_data(element):
            data_dict = {}
            for key, value in element.items():
                if isinstance(value, dict):
                    nested_data = extract_data(value)
                    data_dict.update(nested_data)
                else:
                    data_dict[key] = value
            return data_dict
        
        xml_dict = xmltodict.parse(xml_response)
        entries = xml_dict.get('feed', {}).get('entry', [])
        
        data_dicts = []
        if not isinstance(entries, list):
            entries = [entries]  # Ensure entries is always a list
        
        for entry in entries:
            data_dict = extract_data(entry)
            data_dicts.append(data_dict)

        df = pd.DataFrame(data_dicts)
        return df

    
    def get_functions_list(self):
        url = f'{self.base_url}'

        headers = {
            "X-CSRF-Token": "fetch",
            'Accept': 'application/json'
        }

        response = requests.get(url, headers=headers, auth=HTTPBasicAuth(self.username, self.password))
        if response.status_code == 200:
            try:
                df = pd.DataFrame(json.loads(response.text)['d']['EntitySets'], columns=['EntitySetName'])
                return df
            except json.JSONDecodeError as e:
                print("Error decoding JSON response:", e)
        else:
            print("Request failed with status code:", response.status_code)
            return None

    def get_entity_data(self, entity_set_name):
        return self._get_entity_data(entity_set_name)

    def get_JobInfoSet(self,query_params=None):
        """
        Get job information.

        :param query_params: Dictionary of query parameters for customization.
                            - '$top': Number of records to retrieve.
                            - '$orderby': Order items by property values.
                              Options: 'JOB_NAME', 'JOB_NAME desc', 'JOB_COUNT', 'JOB_COUNT desc',
                                       'STEP_COUNT', 'STEP_COUNT desc', 'IBP_LOG_HANDLE', 'IBP_LOG_HANDLE desc'
                            - '$select': Select properties to be returned.
                              Options: 'JOB_NAME', 'JOB_COUNT', 'STEP_COUNT', 'IBP_LOG_HANDLE'
        :return: Response from the API.
        """
        return self._get_entity_data('/JobInfoSet',query_params)

    def get_xIBPxC_IBPLOGS_TBL(self, query_params=None):
        """
        Fetch data from the /xIBPxC_IBPLOGS_TBL endpoint.

        :param query_params: Dictionary of query parameters for customization. For example:
                            - '$top': Number of records to retrieve.
                            - '$orderby': Order items by property values.
                            Options: 'COLUMN_NAME', 'COLUMN_NAME desc', etc.
                            - '$select': Select properties to be returned.
                            Options: 'COLUMN_NAME1', 'COLUMN_NAME2', etc.
        :return: Response from the API, likely in JSON format.

        """
        return self._get_entity_data('/xIBPxC_IBPLOGS_TBL', query_params)


    def get_xIBPxC_IBP_LOG_ATT(self, query_params=None):
        """
        Fetch data from the /xIBPxC_IBP_LOG_ATT endpoint.
        """
        return self._get_entity_data('/xIBPxC_IBP_LOG_ATT', query_params)

    def get_xIbpxC_log_hdr(self, query_params=None):
        """
        Fetch data from the /xIbpxC_log_hdr endpoint.
        """
        return self._get_entity_data('/xIbpxC_log_hdr', query_params)

    def get_xIBPxC_LOG_TAGS(self, query_params=None):
        """
        Fetch data from the /xIBPxC_LOG_TAGS endpoint.
        """
        return self._get_entity_data('/xIBPxC_LOG_TAGS', query_params)

    def get_xibpxi_Log_Area_Desc_Vh(self, query_params=None):
        """
        Fetch data from the /xibpxi_Log_Area_Desc_Vh endpoint.
        """
        return self._get_entity_data('/xibpxi_Log_Area_Desc_Vh', query_params)

    def get_xibpxi_Log_Area_Vh(self, query_params=None):
        """
        Fetch data from the /xibpxi_Log_Area_Vh endpoint.
        """
        return self._get_entity_data('/xibpxi_Log_Area_Vh', query_params)

    def get_xibpxi_Log_Ext_Id_Vh(self, query_params=None):
        """
        Fetch data from the /xibpxi_Log_Ext_Id_Vh endpoint.
        """
        return self._get_entity_data('/xibpxi_Log_Ext_Id_Vh', query_params)

    def get_xibpxi_Log_Handle_Vh(self, query_params=None):
        """
        Fetch data from the /xibpxi_Log_Handle_Vh endpoint.
        """
        return self._get_entity_data('/xibpxi_Log_Handle_Vh', query_params)

    def get_xibpxi_Log_Status_Vh(self, query_params=None):
        """
        Fetch data from the /xibpxi_Log_Status_Vh endpoint.
        """
        return self._get_entity_data('/xibpxi_Log_Status_Vh', query_params)

    def get_xibpxi_Log_SubArea_Desc_Vh(self, query_params=None):
        """
        Fetch data from the /xibpxi_Log_SubArea_Desc_Vh endpoint.
        """
        return self._get_entity_data('/xibpxi_Log_SubArea_Desc_Vh', query_params)

    def get_xibpxi_Log_subArea_Vh(self, query_params=None):
        """
        Fetch data from the /xibpxi_Log_subArea_Vh endpoint.
        """
        return self._get_entity_data('/xibpxi_Log_subArea_Vh', query_params)

    def get_xibpxi_Log_Username_Vh(self, query_params=None):
        """
        Fetch data from the /xibpxi_Log_Username_Vh endpoint.
        """
        return self._get_entity_data('/xibpxi_Log_Username_Vh', query_params)
