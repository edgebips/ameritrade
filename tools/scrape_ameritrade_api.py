#!/usr/bin/env python3
"""Scrape the TD Ameritrade API Schemas.
"""
__author__ = 'Martin Blais <blais@furius.ca>'
__license__ = "GNU GPLv2"

import logging
import os
import re
import tempfile
import time
import argparse
import json
import logging
import pprint
from os import path
from typing import Any, Dict, List, Tuple, Union

from selenium import webdriver
from selenium.common.exceptions import WebDriverException
from selenium.webdriver.chrome import options
from selenium.webdriver.chrome.webdriver import WebDriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait


def create_driver(driver_exec: str = "/usr/local/bin/chromedriver",
                  headless: bool = False) -> WebDriver:
    """Create web driver instance with all the options."""
    opts = options.Options()
    opts.headless = headless
    return webdriver.Chrome(executable_path=driver_exec, options=opts)


def CleanName(name: str) -> str:
    """Clean up category and function names to CamelCase ids."""
    name = re.sub(r"\band\b", "And", name)
    name = re.sub(r"\bfor\b", "For", name)
    name = re.sub(r" a ", " A ", name)
    return re.sub(r" ", "", name)


def GetEndpoints(driver: WebDriver, trace: bool = False) -> Dict[str, str]:
    """Get a list of endpoints to fetch."""
    driver.get("https://developer.tdameritrade.com/apis")
    elem = driver.find_element_by_class_name('view-smartdocs-models')
    categories = {}
    for row in elem.find_elements_by_class_name('views-row'):
        category = CleanName(row.text.splitlines()[0])
        link = row.find_element_by_tag_name('a').get_attribute('href')
        categories[category] = link
    if trace:
        pprint.pprint(categories)

    # Process each of the categories.
    endpoints = []
    for catname, catlink in sorted(categories.items()):
        logging.info("Getting %s", catlink)
        driver.get(catlink)
        for row in driver.find_elements_by_class_name('views-row'):
            link = row.find_element_by_tag_name('a').get_attribute('href')
            method, funcname, apilink = row.text.splitlines()[:3]
            funcname = CleanName(funcname.strip())
            endpoints.append((catname, funcname, method, apilink, link))
    if trace:
        pprint.pprint(endpoints)

    return endpoints


def GetExampleAndSchema(driver: WebDriver) -> Tuple[str, str]:
    """Extract JSON schema and examples from an endpoint page."""
    # Attempt to get the data from the bottom table.
    example = driver.execute_script('return jQuery("textarea.payload_text").val();')
    schema = driver.execute_script('return jQuery("textarea.payload_text_schema").val();')
    if example is None:
        # Attempt to get the date from the table on the right side.
        example = driver.execute_script('return jQuery("textarea#response_body_example").val();')
        schema = driver.execute_script('return jQuery("textarea#response_body_schema").val();')
        if example is None:
            # Give up, there's probably no table.
            example = ''
            schema = ''
    return example, schema


def GetErrorCodes(driver: WebDriver) -> Dict[int, str]:
    """Extract a table of code -> message string."""
    elem = driver.find_element_by_class_name('table-error-codes')
    errcodes = {}
    for tr in elem.find_elements_by_class_name('listErrorCodes'):
        code, message = [td.text for td in tr.find_elements_by_tag_name('td')]
        errcodes[int(code)] = message
    return errcodes


def GetQueryParameters(driver: WebDriver) -> Dict[str, str]:
    """Extract the query parameters from the page."""
    query_params = {}
    try:
        div = driver.find_element_by_id('queryTable')
    except WebDriverException:
        return query_params
    table = div.find_element_by_tag_name('table')
    for row in table.find_elements_by_tag_name('tr'):
        row = [td.text for td in row.find_elements_by_tag_name('td')]
        if not row:
            continue
        name, description = row[0], row[2]
        query_params[name] = description
    return query_params


def WriteFile(filename: str, contents: Union[str, Any]):
    """Write a file, creating dir, conditionally, and with some debugging."""
    if not isinstance(contents, str):
        pprint.pprint(contents)
    logging.info("Writing: %s", filename)
    os.makedirs(path.dirname(filename), exist_ok=True)
    with open(filename, 'w') as ofile:
        ofile.write(contents)


def main():
    logging.basicConfig(level=logging.INFO, format='%(levelname)-8s: %(message)s')
    parser = argparse.ArgumentParser(description=__doc__.strip())
    parser.add_argument('output', help='Output directory to produce scraped API')
    args = parser.parse_args()

    if not path.exists(args.output):
        os.makedirs(args.output)

    driver = create_driver()
    logging.info("Getting %s", "https://developer.tdameritrade.com/apis")

    # Find the categories and their top-level links to each of the available API
    # endpoints.
    endpoints = GetEndpoints(driver)

    # Process each endpoint page, fetching related data with minimal process
    # (we'll post-process, to minimize traffic on the site from re-runs).
    for catname, funcname, method, apilink, link in endpoints:
        logging.info("Processing: %s %s", method, link)

        # Open the page.
        driver.get(link)

        # Fetch the schema and example.
        example, schema = GetExampleAndSchema(driver)

        # Get the table of error codes.
        errcodes = GetErrorCodes(driver)
        errcodes_json = json.dumps(errcodes, sort_keys=True, indent=4)

        # Get the query parameters.
        query_params = GetQueryParameters(driver)
        request = {
            'method': method,
            'link': apilink,
            'query_params': query_params,
        }
        request_json = json.dumps(request, sort_keys=True, indent=4)

        # Write out the output files.
        dirname = path.join(args.output, catname, funcname)
        WriteFile(path.join(dirname, "request.json"), request_json)
        WriteFile(path.join(dirname, "response.json"), schema)
        WriteFile(path.join(dirname, "errcodes.json"), errcodes_json)
        WriteFile(path.join(dirname, "example.json"), example)

    logging.info("Done")
    #import pdb; pdb.set_trace()


if __name__ == '__main__':
    main()
