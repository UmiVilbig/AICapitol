"POC XML parsing"

import pandas
import io

"""
Workflow:
1. hit https://disclosures-clerk.house.gov/public_disc/financial-pdfs/2024FD.zip and save
2. unzip 2024FD.zip
3. parse <YEAR>FD.xml to dataframe
4. filter by sort by DocID (ascending: false)
5. filter to start with 200
6. get first index and fetch https://disclosures-clerk.house.gov/public_disc/ptr-pdfs/2024/<ID>.pdf

"""
