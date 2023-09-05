# Ibp2py - Python library for SAP IBP

This is a Python library designed to make it easier to interact with the SAP Integrated Business Planning (IBP) API.

## Installation

You can install ibpy using pip:

```bash
pip install ibpy2py
```
## Usage

To use ibpy, first create an instance of the `ibpy` class using your SAP IBP username and password:

```python
from ibpy import ibpy  
username = "YOUR_IBP_USERNAME" 
password = "YOUR_IBP_PASSWORD" 
host = 'YOUR_HOST_URL' 
connection = Ibp2py(username, password, host)
```

### Extracting Master Data

Here is an example of how to extract master data:
Method -> MASTER_DATA_API_SRV


```python
PlanningAreaID = 'SAP01' 
VersionID = "BASE" 
MasterDataTypeID = "M3LOCATION" 
PlanningAreaDescr = "Planning" 
VersionName = "Base Line" 
select = '*' 
data = connection.masterdata(MasterDataTypeID, select=select, PlanningAreaID=PlanningAreaID, VersionID=VersionID, PlanningAreaDescr=PlanningAreaDescr, VersionName=VersionName)
```

### Extracting Telemetry Data
Method -> *AddInLogon* (MtrgActyExcelAddInLogon)
Method -> *AddInLogon* (MtrgActyExcelAddInPlanningView)

module -> Method


Here is an example of how to extract telemetry data:

```python
data = connection.telemetry('PlanningView', module)
```
### Extracting Key Figure Data
Method -> 1 (PLANNING_DATA_API_SRV)
Method -> 2 (EXTRACT_ODATA_SRV)

modulo -> Method

Here is an example of how to extract key figure data:

```python
filters="(PERIODID0_TSTAMP ge datetime'2023-04-01T00:00:00' and PERIODID0_TSTAMP lt datetime'2023-07-02T00:00:00')"+ " and CONSENSUSDEMAND gt 0" 
PlanningAreaID = 'SAP01' 
MasterData = 'PRDID,CUSTID' 
KeyFigures = 'CONSENSUSDEMAND' 
data = connection.keyfigure(PlanningAreaID, MasterData, KeyFigures,modulo = modulo,filters=filters)
```
## Contact Information

For any issues or queries related to ibpy2py, feel free to reach out:

- Author: Pedro Rastha
- Email: [pedrorastha@gmail.com](mailto:pedrorastha@gmail.com)
- LinkedIn: [@pedrorastha](https://www.linkedin.com/in/pedrorastha)


## Contributing

Pull requests are welcome. For major changes, please open an issue first to discuss what you would like to change.

## License

[Apache License 2.0](https://choosealicense.com/licenses/apache-2.0/)

**Note:** This library is open source and is not sponsored or supported by SAP.
