from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
import httpx
from datetime import datetime

app = FastAPI(
    title="Global Population API",
    description="Global population statistics including total population, growth rates, density, and demographics for countries worldwide. Powered by World Bank Open Data.",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

WB_BASE = "https://api.worldbank.org/v2"

INDICATORS = {
    "population":      {"id": "SP.POP.TOTL",     "name": "Total Population",           "unit": "Persons"},
    "growth":          {"id": "SP.POP.GROW",      "name": "Population Growth Rate",     "unit": "Annual %"},
    "density":         {"id": "EN.POP.DNST",      "name": "Population Density",         "unit": "People per sq km"},
    "birth_rate":      {"id": "SP.DYN.CBRT.IN",   "name": "Birth Rate",                 "unit": "Per 1,000 people"},
    "death_rate":      {"id": "SP.DYN.CDRT.IN",   "name": "Death Rate",                 "unit": "Per 1,000 people"},
    "urban_pop":       {"id": "SP.URB.TOTL.IN.ZS", "name": "Urban Population",          "unit": "% of Total"},
    "life_expectancy": {"id": "SP.DYN.LE00.IN",   "name": "Life Expectancy at Birth",   "unit": "Years"},
    "fertility_rate":  {"id": "SP.DYN.TFRT.IN",   "name": "Fertility Rate",             "unit": "Births per Woman"},
}

COUNTRIES = {
    "WLD": "World",
    "USA": "United States",
    "CHN": "China",
    "IND": "India",
    "IDN": "Indonesia",
    "PAK": "Pakistan",
    "BRA": "Brazil",
    "NGA": "Nigeria",
    "BGD": "Bangladesh",
    "RUS": "Russia",
    "ETH": "Ethiopia",
    "MEX": "Mexico",
    "JPN": "Japan",
    "PHL": "Philippines",
    "EGY": "Egypt",
    "COD": "DR Congo",
    "VNM": "Vietnam",
    "IRN": "Iran",
    "TUR": "Turkey",
    "DEU": "Germany",
    "THA": "Thailand",
    "GBR": "United Kingdom",
    "FRA": "France",
    "KOR": "South Korea",
    "ZAF": "South Africa",
    "TZA": "Tanzania",
    "COL": "Colombia",
    "KEN": "Kenya",
    "ARG": "Argentina",
    "ESP": "Spain",
    "ITA": "Italy",
}


async def fetch_wb_country(country_code: str, indicator_id: str, limit: int = 10):
    url = f"{WB_BASE}/country/{country_code}/indicator/{indicator_id}"
    params = {"format": "json", "mrv": limit, "per_page": limit}
    async with httpx.AsyncClient(timeout=15) as client:
        res = await client.get(url, params=params)
        data = res.json()
    if not data or len(data) < 2:
        return []
    records = data[1] or []
    return [
        {"year": str(r["date"]), "value": r["value"]}
        for r in records
        if r.get("value") is not None
    ]


async def fetch_wb_all_countries(indicator_id: str, limit: int = 1):
    """Fetch latest value for all countries"""
    url = f"{WB_BASE}/country/all/indicator/{indicator_id}"
    params = {"format": "json", "mrv": limit, "per_page": 300}
    async with httpx.AsyncClient(timeout=20) as client:
        res = await client.get(url, params=params)
        data = res.json()
    if not data or len(data) < 2:
        return []
    records = data[1] or []
    results = []
    for r in records:
        if r.get("value") is not None and r.get("countryiso3code"):
            results.append({
                "country_code": r["countryiso3code"],
                "country": r["country"]["value"],
                "year": str(r["date"]),
                "value": r["value"],
            })
    return results


@app.get("/")
def root():
    return {
        "api": "Global Population API",
        "version": "1.0.0",
        "provider": "GlobalData Store",
        "source": "World Bank Open Data",
        "endpoints": [
            "/summary", "/population", "/growth", "/density",
            "/birth-rate", "/death-rate", "/urban-population",
            "/life-expectancy", "/fertility-rate", "/rankings"
        ],
        "countries": list(COUNTRIES.keys()),
        "updated_at": datetime.utcnow().isoformat() + "Z",
    }


@app.get("/summary")
async def summary(
    country: str = Query(default="WLD", description="ISO3 country code (default: WLD = World)"),
    limit: int = Query(default=5, ge=1, le=30)
):
    """All key population indicators for a country or the world"""
    country = country.upper()
    results = {}
    for key, meta in INDICATORS.items():
        results[key] = await fetch_wb_country(country, meta["id"], limit)
    formatted = {
        key: {
            "name": INDICATORS[key]["name"],
            "unit": INDICATORS[key]["unit"],
            "data": results[key],
        }
        for key in INDICATORS
    }
    return {
        "country_code": country,
        "country": COUNTRIES.get(country, country),
        "source": "World Bank Open Data",
        "updated_at": datetime.utcnow().isoformat() + "Z",
        "indicators": formatted,
    }


@app.get("/population")
async def population(
    country: str = Query(default="WLD", description="ISO3 country code"),
    limit: int = Query(default=10, ge=1, le=60)
):
    """Total population by country or world"""
    country = country.upper()
    data = await fetch_wb_country(country, "SP.POP.TOTL", limit)
    return {
        "indicator": "Total Population",
        "series_id": "SP.POP.TOTL",
        "unit": "Persons",
        "frequency": "Annual",
        "country_code": country,
        "country": COUNTRIES.get(country, country),
        "source": "World Bank",
        "updated_at": datetime.utcnow().isoformat() + "Z",
        "data": data,
    }


@app.get("/growth")
async def growth(
    country: str = Query(default="WLD", description="ISO3 country code"),
    limit: int = Query(default=10, ge=1, le=60)
):
    """Population growth rate (annual %)"""
    country = country.upper()
    data = await fetch_wb_country(country, "SP.POP.GROW", limit)
    return {
        "indicator": "Population Growth Rate",
        "series_id": "SP.POP.GROW",
        "unit": "Annual %",
        "frequency": "Annual",
        "country_code": country,
        "country": COUNTRIES.get(country, country),
        "source": "World Bank",
        "updated_at": datetime.utcnow().isoformat() + "Z",
        "data": data,
    }


@app.get("/density")
async def density(
    country: str = Query(default="WLD", description="ISO3 country code"),
    limit: int = Query(default=10, ge=1, le=60)
):
    """Population density (people per sq km of land area)"""
    country = country.upper()
    data = await fetch_wb_country(country, "EN.POP.DNST", limit)
    return {
        "indicator": "Population Density",
        "series_id": "EN.POP.DNST",
        "unit": "People per sq km",
        "frequency": "Annual",
        "country_code": country,
        "country": COUNTRIES.get(country, country),
        "source": "World Bank",
        "updated_at": datetime.utcnow().isoformat() + "Z",
        "data": data,
    }


@app.get("/birth-rate")
async def birth_rate(
    country: str = Query(default="WLD", description="ISO3 country code"),
    limit: int = Query(default=10, ge=1, le=60)
):
    """Crude birth rate (births per 1,000 people)"""
    country = country.upper()
    data = await fetch_wb_country(country, "SP.DYN.CBRT.IN", limit)
    return {
        "indicator": "Birth Rate",
        "series_id": "SP.DYN.CBRT.IN",
        "unit": "Per 1,000 people",
        "frequency": "Annual",
        "country_code": country,
        "country": COUNTRIES.get(country, country),
        "source": "World Bank",
        "updated_at": datetime.utcnow().isoformat() + "Z",
        "data": data,
    }


@app.get("/death-rate")
async def death_rate(
    country: str = Query(default="WLD", description="ISO3 country code"),
    limit: int = Query(default=10, ge=1, le=60)
):
    """Crude death rate (deaths per 1,000 people)"""
    country = country.upper()
    data = await fetch_wb_country(country, "SP.DYN.CDRT.IN", limit)
    return {
        "indicator": "Death Rate",
        "series_id": "SP.DYN.CDRT.IN",
        "unit": "Per 1,000 people",
        "frequency": "Annual",
        "country_code": country,
        "country": COUNTRIES.get(country, country),
        "source": "World Bank",
        "updated_at": datetime.utcnow().isoformat() + "Z",
        "data": data,
    }


@app.get("/urban-population")
async def urban_population(
    country: str = Query(default="WLD", description="ISO3 country code"),
    limit: int = Query(default=10, ge=1, le=60)
):
    """Urban population as % of total population"""
    country = country.upper()
    data = await fetch_wb_country(country, "SP.URB.TOTL.IN.ZS", limit)
    return {
        "indicator": "Urban Population",
        "series_id": "SP.URB.TOTL.IN.ZS",
        "unit": "% of Total Population",
        "frequency": "Annual",
        "country_code": country,
        "country": COUNTRIES.get(country, country),
        "source": "World Bank",
        "updated_at": datetime.utcnow().isoformat() + "Z",
        "data": data,
    }


@app.get("/life-expectancy")
async def life_expectancy(
    country: str = Query(default="WLD", description="ISO3 country code"),
    limit: int = Query(default=10, ge=1, le=60)
):
    """Life expectancy at birth (years)"""
    country = country.upper()
    data = await fetch_wb_country(country, "SP.DYN.LE00.IN", limit)
    return {
        "indicator": "Life Expectancy at Birth",
        "series_id": "SP.DYN.LE00.IN",
        "unit": "Years",
        "frequency": "Annual",
        "country_code": country,
        "country": COUNTRIES.get(country, country),
        "source": "World Bank",
        "updated_at": datetime.utcnow().isoformat() + "Z",
        "data": data,
    }


@app.get("/fertility-rate")
async def fertility_rate(
    country: str = Query(default="WLD", description="ISO3 country code"),
    limit: int = Query(default=10, ge=1, le=60)
):
    """Total fertility rate (births per woman)"""
    country = country.upper()
    data = await fetch_wb_country(country, "SP.DYN.TFRT.IN", limit)
    return {
        "indicator": "Fertility Rate",
        "series_id": "SP.DYN.TFRT.IN",
        "unit": "Births per Woman",
        "frequency": "Annual",
        "country_code": country,
        "country": COUNTRIES.get(country, country),
        "source": "World Bank",
        "updated_at": datetime.utcnow().isoformat() + "Z",
        "data": data,
    }


@app.get("/rankings")
async def rankings(
    indicator: str = Query(default="population", description="Indicator: population, growth, density, birth_rate, death_rate, urban_pop, life_expectancy, fertility_rate"),
    limit: int = Query(default=20, ge=1, le=50)
):
    """Global country rankings by population indicator"""
    if indicator not in INDICATORS:
        return {"error": f"Unknown indicator. Choose from: {list(INDICATORS.keys())}"}
    meta = INDICATORS[indicator]
    data = await fetch_wb_all_countries(meta["id"], 1)
    # Sort by value descending, exclude aggregates
    sorted_data = sorted(
        [d for d in data if len(d["country_code"]) == 3],
        key=lambda x: x["value"] if x["value"] is not None else 0,
        reverse=True
    )
    ranked = [{"rank": i + 1, **entry} for i, entry in enumerate(sorted_data[:limit])]
    return {
        "indicator": meta["name"],
        "series_id": meta["id"],
        "unit": meta["unit"],
        "source": "World Bank",
        "updated_at": datetime.utcnow().isoformat() + "Z",
        "rankings": ranked,
    }
