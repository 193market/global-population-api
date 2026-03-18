# Global Population API

Global population statistics including total population, growth rates, density, birth rates, death rates, urban population, life expectancy, and fertility rates for countries worldwide. Powered by World Bank Open Data.

## Endpoints

| Endpoint | Description |
|----------|-------------|
| `GET /` | API info and available endpoints |
| `GET /summary` | All population indicators snapshot for a country |
| `GET /population` | Total population |
| `GET /growth` | Population growth rate (annual %) |
| `GET /density` | Population density (people per sq km) |
| `GET /birth-rate` | Crude birth rate (per 1,000 people) |
| `GET /death-rate` | Crude death rate (per 1,000 people) |
| `GET /urban-population` | Urban population (% of total) |
| `GET /life-expectancy` | Life expectancy at birth (years) |
| `GET /fertility-rate` | Total fertility rate (births per woman) |
| `GET /rankings` | Global country rankings by indicator |

## Query Parameters

| Parameter | Description | Default |
|-----------|-------------|---------|
| `country` | ISO3 country code (e.g., USA, CHN, WLD for World) | `WLD` |
| `limit` | Number of years to return (1–60) | `10` |
| `indicator` | For /rankings: population, growth, density, etc. | `population` |

## Supported Countries

Includes 190+ countries. Use ISO3 codes: `USA`, `CHN`, `IND`, `BRA`, `DEU`, `JPN`, `GBR`, `WLD` (World), etc.

## Data Source

World Bank Open Data
https://data.worldbank.org/indicator

## Authentication

Requires `X-RapidAPI-Key` header via RapidAPI.
