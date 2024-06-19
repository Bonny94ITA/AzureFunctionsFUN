# Azure FunctionsFUN - Horoscope Email Service

This project implements an Azure Functions service that sends daily horoscope emails. The function is triggered by Azure Data Factory, uses OpenAI's GPT API for content enrichment, and performs web scraping to retrieve horoscope data.

## Prerequisites

- Python 3.8 or higher
- Azure Functions Core Tools
- An email account for sending emails (configured in `config.py`)
- OpenAI API Key

## Resources in Azure

<p align="center">
  <img src="https://github.com/Bonny94ITA/AzureFunctionsFUN/assets/60448424/43ede218-7fb1-4482-b025-cde79f1899c1" alt="doc2">
</p>

## Architecture

<p align="center">
  <img src="https://github.com/Bonny94ITA/AzureFunctionsFUN/assets/60448424/6c9b8c0d-47a9-4f66-8492-feaeaecba8e4" alt="doc2">
</p>

## Functionality
### Web Scraping
The get_horoscope function scrapes the daily horoscope from the specified website using BeautifulSoup.

### GPT API Integration
The get_horoscope_gpt function enriches the scraped horoscope with additional thematic content using the OpenAI GPT API.

### Email Sending
The send_email function sends the generated and enriched horoscope via email using the SMTP protocol.

## Integration with Azure Data Factory
This Azure Function is designed to be triggered by Azure Data Factory (ADF). ADF can be configured to invoke the function on a schedule or based on other data integration workflows, ensuring that horoscope emails are sent out daily or as needed.
