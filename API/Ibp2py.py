"""
-------------------------------------------------------------------------------
Ibp2py: SAP Data Retrieval and Processing Library
-------------------------------------------------------------------------------
Author: Pedro Rastha
Email : pedrorastha@gmail.com
Date  : 26/07/2023
Linkedin:@pedrorastha
Site: www.ocultai.com
-------------------------------------------------------------------------------

This library contains a class, Ibp2py, designed to fetch data from various 
modules of an SAP instance. The class includes the following functionalities:

    1. Establishing a connection with the SAP instance.
    2. Sending HTTP requests to the SAP server.
    3. Processing XML or JSON responses from the server.
    4. Logging function calls for debugging and tracking.

The ibpy class offers methods to fetch and process data from 
Master Data, Telemetry, and Key Figures modules. The data is processed and 
transformed into convenient data structures like pandas DataFrame or 
list of dictionaries for further use.

Note: This library requires the `requests`, `pandas`, `xml.etree.ElementTree`, 
`pathlib`, `json`, and `logging` libraries.

Copyright 2023 Pedro Rastha

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.

This library is open source and is not sponsored or supported by SAP.
"""

# Import necessary modules
import requests
from requests.auth import HTTPBasicAuth
import xml.etree.ElementTree as ET
import pandas as pd
from pathlib import Path  # Import pathlib to work with file paths
import json
import logging

# Set up logging with a basic configuration
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

class Ibp2py:
    """
    A class used to interact with SAP IBP.

    Attributes
    ----------
    username : str
        The username for Communication Users.
    password : str
        The password for Communication Users.
    base_url : str
        The base URL for SAP IBP host plus API path.

    Methods
    -------
    __get_data(entity_set, headers, **kwargs)
        Sends a GET request to SAP IBP and returns the response content.
    __process_response(response, export=False)
        Processes the XML response from SAP IBP and returns a DataFrame.
    masterdata(MasterData, select, page_size=5000, total_records=None, **kwargs)
        Retrieves and processes master data from SAP IBP.
    telemetry(module)
        Retrieves and processes telemetry data from SAP IBP.
    keyfigure(PlanningAreaID, MasterData, KeyFigures, page_size=5000, total_records=None, module=1, **kwargs)
        Retrieves and processes key figure data from SAP IBP.
    """
    def __init__(self, username, password, host):
        """
        Constructs all the necessary attributes for the ibpy object.

        Parameters
        ----------
            username : str
                The username for Communication Users.
            password : str
                The password for Communication Users.
            host : str
                The base URL for SAP IBP host plus API path.
        """
        self.username = username
        self.password = password
        self.default_base_url = f'https://{host}/sap/opu/odata/IBP/'
        self.base_url = self.default_base_url 
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(logging.INFO)

    # Define a decorator for logging function calls
    def log_function_call(func):
        """
        Decorator function for logging function calls.

        Parameters:
        func (function): The function to be wrapped and logged.

        Returns:
        wrapper (function): The wrapped function that includes logging functionality.
        """
        def wrapper(*args, **kwargs):
            self = args[0]
            self.logger.info(f"Calling {func.__name__} with args: {args[1:]}, kwargs: {kwargs}")
            return func(*args, **kwargs)
        return wrapper

    # Define a private function to get data from SAP
    @log_function_call
    def __get_data(self, entity_set, headers, **kwargs):
        """
        Sends a GET request to SAP IBP and returns the response content.

        Parameters:
        entity_set (str): The endpoint for the SAP service.
        headers (dict): HTTP headers to include in the request.
        
        **kwargs: Optional parameters to include in the request. Possible parameters are:
            "$select": Properties to be included in the response.
            "$filter": Filter condition to restrict the returned resources.
            "$top": Maximum number of items to return in the response.
            "$skip": Number of items to skip before starting to return items.
            "$format": Request the response in a specific media format.
            "$orderby": Properties to sort the results by.
            "$expand": Related resources to be included in line with retrieved resources.
            "$count": Request a count of the matching resources included with the resources in the response.
            "$search": Restrict the result to include only those entities matching the search expression.
            "$inlinecount": Request a count of the matching resources included with the resources in the response.
            "$skiptoken": Token value for server-driven paging.

        Returns:
        response.content (str): The response content from the SAP service.
        """
        url = self.base_url + entity_set

        params = {
            "$select": kwargs.get("select", None),
            "$filter": kwargs.get("filters", None),
            "$top": kwargs.get("top", None),
            "$skip": kwargs.get("skip", None),
            "$format": kwargs.get("format", None),
            "$orderby": kwargs.get("orderby", None),
            "$expand": kwargs.get("expand", None),
            "$count": kwargs.get("count", None),
            "$search": kwargs.get("search", None),
            "$inlinecount": kwargs.get("inlinecount", None),
            "$skiptoken": kwargs.get("skiptoken", None),
        }

        # Remove None values from the parameters
        params = {key: value for key, value in params.items() if value is not None}

        try:
            response = requests.get(url, params=params, headers=headers, auth=HTTPBasicAuth(self.username, self.password))
            response.raise_for_status()
        except requests.exceptions.RequestException as e:
            self.logger.error(f"Failed to send GET request to {url}: {e}")
            raise
        except requests.exceptions.HTTPError as e:
            if response.status_code == 401:
                self.logger.error("Failed to authenticate with the server. Please check your username and password.")
            else:
                self.logger.error(f"Server responded with an error status: {e}")
            raise

        print(f"Final URL sent: {response.url}")
        print(f"Params: {params}")

        return response.content

    # Define a private function to process the response from SAP
    @log_function_call
    def __process_response(self, response, export = False):
        """
        Process the XML or JSON response from the server and convert it to a pandas DataFrame.

        Parameters:
        response (str): The XML or JSON response string from the server.
        export (bool, optional): Whether to export the data to a CSV file. Defaults to False.

        Returns:
        df (DataFrame): A pandas DataFrame containing the processed data.
        """
        try:
            root = ET.fromstring(response)
        except ET.ParseError as e:
            self.logger.error(f"Failed to parse XML response: {e}")
            raise

        namespaces = {
            'app': 'http://www.w3.org/2007/app',
            'atom': 'http://www.w3.org/2005/Atom',
            'm': 'http://schemas.microsoft.com/ado/2007/08/dataservices/metadata',  # Add the correct 'm' namespace here
        }

        data = []

        for entry in root.findall('atom:entry', namespaces):
            record = {}
            content_elem = entry.find('atom:content', namespaces)
            if content_elem is not None:
                properties_elem = content_elem.find('m:properties', namespaces)
                if properties_elem is not None:
                    for column_elem in properties_elem:
                        column_name = column_elem.tag.split('}')[-1]  # Extract the element name without the namespace
                        record[column_name] = column_elem.text
                data.append(record)

        try:
            df = pd.DataFrame(data)
        except ValueError as e:
            self.logger.error(f"Failed to create DataFrame: {e}")
            raise

        if export:
            try:
                desktop_path = Path.home() / "Desktop"  # Get the path to the desktop directory
                filename = "output.csv"  # Specify the filename for the CSV file

                # Save the DataFrame to a CSV file on the desktop
                file_path = desktop_path / filename
                df.to_csv(file_path, index=False)
            except Exception as e:
                self.logger.error(f"Failed to save DataFrame to CSV: {e}")
                raise

        return df  

    # Define a function to get master data from SAP
    @log_function_call
    def masterdata(self, MasterData, select, page_size=5000, total_records=None, **kwargs):
        """
        Fetches master data from the specified SAP module.

        Parameters:
        MasterData (str): The type of master data to be retrieved.
        select (str): The fields to be retrieved.
        page_size (int, optional): The number of records to fetch in each request. Defaults to 5000.
        total_records (int, optional): The total number of records to fetch. If None, fetches all available records.
        **kwargs (dict, optional): Additional parameters to pass to the __get_data method. Can include the following keys:
            - "PlanningAreaID": The ID of the planning area.
            - "VersionID": The ID of the version.
            - "PlanningAreaDescr": The description of the planning area.
            - "VersionName": The name of the version.
            - "filters": Any filters to apply to the data retrieval.
            - "top": The maximum number of records to return.
            - "skip": The number of records to skip before starting to return records.
            - "format": The format of the data to return.
            - "orderby": The order in which to return the records.
            - "expand": Any additional fields to expand in the returned data.
            - "count": Whether to include a count of the total number of records.
            - "search": Any search criteria to apply to the data retrieval.
            - "inlinecount": Whether to include an inline count of the total number of records.
            - "skiptoken": A token to use for retrieving the next page of data.

        Returns:
        data (DataFrame): A pandas DataFrame containing the fetched master data.
        """
        Module = 'MASTER_DATA_API_SRV/'
        entity_set = Module + MasterData + '?'

        # Define os valores padrão dos parâmetros opcionais
        headers = {
            "PlanningAreaID": kwargs.get("PlanningAreaID"),
            "VersionID": kwargs.get("VersionID"), #ANUAL
            "MasterDataTypeID": MasterData,
            #"PlanningAreaDescr": kwargs.get("PlanningAreaDescr"),
            "VersionName": kwargs.get("VersionName"),
        }

        
        filters = kwargs.get("filters", None)
        top = kwargs.get("top", None)
        skip = kwargs.get("skip", None)
        format = kwargs.get("format", None)
        orderby = kwargs.get("orderby", None)
        expand = kwargs.get("expand", None)
        count = kwargs.get("count", None)
        search = kwargs.get("search", None)
        inlinecount = kwargs.get("inlinecount", None)
        skiptoken = kwargs.get("skiptoken", None)

        skip = 0
        data = []  # Initialize an empty list to hold all data
        
        while total_records is None or skip < total_records:
            if total_records is not None:
                top = min(page_size, total_records - skip)  # Don't request more records than remaining
            else:
                top = page_size

            try:
                response = self.__get_data(entity_set, headers, page_size=page_size, total_records=total_records, select=select, filters=filters, top=top, skip=skip, format=format, 
                                        orderby=orderby, expand=expand, count=count, search=search, inlinecount=inlinecount, 
                                        skiptoken=skiptoken)
            except requests.HTTPError as e:
                self.logger.error(f"HTTP request failed: {e}")
                raise

            # Process the data
            try:
                df = self.__process_response(response, export=False)
            except ET.ParseError as e:
                self.logger.error(f"Failed to parse XML response: {e}")
                raise
            except ValueError as e:
                self.logger.error(f"Failed to create DataFrame: {e}")
                raise

            # If we got less data than the page size, we've reached the end
            if len(df) < top:
                data.append(df)
                break

            data.append(df)
            # Move to the next page
            skip += top

        # Concatenate all data into a single DataFrame
        try:
            data = pd.concat(data, ignore_index=True)
        except ValueError as e:
            self.logger.error(f"Failed to concatenate DataFrames: {e}")
            raise

        return data
    # Define a function to get telemetry data from SAP
    @log_function_call
    def telemetry (self, module):
        """
        Fetches telemetry data from the specified SAP module.

        Parameters:
        module (str): The module from which to retrieve telemetry data. 
                      This can be either 'PlanningView' or 'AddInLogon'.

        Returns:
        extracted_data (list): A list of dictionaries containing the fetched telemetry data. 
                                Each dictionary represents a record of telemetry data.
        
        Note: The function temporarily changes the base_url instance variable to retrieve data from a different API endpoint. 
              The base_url is reset to its default value at the end of the function.
        """
        self.base_url = 'https://my301284-api.scmibp1.ondemand.com/sap/opu/odata4/ibp/api_meteringactivity/srvd_a2x/ibp/api_meteringactivity/0001/'

        if(module == 'PlanningView'):
            modulo_s ='MtrgActyExcelAddInPlanningView?%24select=ActivityID%2CPlanningAreaID&%24top=50'
        elif(module == 'AddInLogon'):
            modulo_s = 'MtrgActyExcelAddInLogon?%24select=ActivityID%2CPlanningAreaID&%24top=50'

        entity_set = modulo_s

        headers = {
            "config_authType": "Basic",
            "config_packageName": "SAPIBPTelemetry",
            "config_actualUrl": "https://my301284-api.scmibp1.ondemand.com/sap/opu/odata4/ibp/api_meteringactivity/srvd_a2x/ibp/api_meteringactivity/0001/",
            "config_urlPattern": "https://{host}/sap/opu/odata4/ibp/api_meteringactivity/srvd_a2x/ibp/api_meteringactivity/0001/",
            "config_apiName": "IBP_Telemetry_ODataService",
            "DataServiceVersion": "2.0",
            "Accept": "application/json"
        }

        try:
            response = self.__get_data(entity_set, headers)
        except requests.HTTPError as e:
            self.logger.error(f"HTTP request failed: {e}")
            raise

        try:
            data = json.loads(response)
        except json.JSONDecodeError as e:
            self.logger.error(f"Failed to decode JSON response: {e}")
            raise

        extracted_data = []
        for item in data['value']:
            record = {}
            for key, value in item.items():
                record[key] = value
            extracted_data.append(record)

        self.base_url = self.default_base_url

        return extracted_data
    # Define a function to get key figures from SAP
    @log_function_call
    def keyfigure(self, PlanningAreaID, MasterData, KeyFigures, page_size=5000, total_records=None, module=1, **kwargs):
        """
        Fetches key figures data from SAP based on the provided parameters.

        Parameters:
        PlanningAreaID (str): The ID of the planning area.
        MasterData (str): The master data to select.
        KeyFigures (str): The key figures to select.
        page_size (int, optional): The number of records to fetch in a single request. Default is 5000.
        total_records (int, optional): The total number of records to fetch. If None, fetch all records. Default is None.
        module (int, optional): The module from which to fetch data. Default is 1.
        **kwargs: Additional parameters to filter the data.
            The additional parameters can be any of the following:
            filters (str): The conditions to filter the data.
            top (int): The number of records to return.
            skip (int): The number of records to skip from the beginning.
            format (str): The format of the returned data.
            orderby (str): The field to order the data by.
            expand (str): The related entities to include in the data.
            count (bool): Whether to include a count of the returned records.
            search (str): The text to search for in the data.
            inlinecount (str): The count of records to include in the response.
            skiptoken (str): The token to use for skipping records.
        Returns:
        data (DataFrame): A pandas DataFrame containing the fetched key figures data.
        """
        modulo = 'PLANNING_DATA_API_SRV/' 
        modulo_ = 'EXTRACT_ODATA_SRV/'

        if(module == 1):
            modulo = modulo
        elif(module == 2):
            modulo = modulo_ 

        headers = {
            "X-CSRF-Token": "fetch",
            "Content-Type": "application/json"
        }

        entity_set = modulo + PlanningAreaID + '?'

        select = MasterData + ',' + KeyFigures

        filters = kwargs.get("filters", None)
        top = kwargs.get("top", None)
        skip = kwargs.get("skip", None)
        format = kwargs.get("format", None)
        orderby = kwargs.get("orderby", None)
        expand = kwargs.get("expand", None)
        count = kwargs.get("count", None)
        search = kwargs.get("search", None)
        inlinecount = kwargs.get("inlinecount", None)
        skiptoken = kwargs.get("skiptoken", None)

        try:
            skip = 0
            data = []  # Initialize an empty list to hold all data

            while total_records is None or skip < total_records:
                if total_records is not None:
                    top = min(page_size, total_records - skip)  # Don't request more records than remaining
                else:
                    top = page_size

                response = self.__get_data(entity_set, headers, page_size=page_size, total_records=total_records, select=select, filters=filters, top=top, skip=skip, format=format, 
                                    orderby=orderby, expand=expand, count=count, search=search, inlinecount=inlinecount, 
                                    skiptoken=skiptoken)

                # Process the data
                df = self.__process_response(response, export=False)

                # If we got less data than the page size, we've reached the end
                if len(df) < top:
                    data.append(df)
                    break

                data.append(df)
                # Move to the next page
                skip += top

        except Exception as e:
            self.logger.error(f"Error in retrieving key figures: {e}")
            raise

        # Concatenate all data into a single DataFrame
        data = pd.concat(data, ignore_index=True)

        return data

    @log_function_call
    def post_keyfigure(self, PlanningAreaID, MasterData, KeyFigures, data, module=1):
        """
        Posts data to a specified key figure in SAP.

        Parameters:
        PlanningAreaID (str): The ID of the planning area.
        MasterData (str): The master data to select.
        KeyFigures (str): The key figures to select.
        data (dict): The data to be posted. This should be a dictionary where the keys match the fields in the key figure.
        module (int, optional): The module to which to post data. Default is 1.

        Returns:
        response (Response): The response from the server after posting the data.
        """
        pass
