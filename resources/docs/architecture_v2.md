# Ocean Report Architecutre 2.0

What I am trying to build

## What I would build


```plaintext
src/
└── ocean_report/
    ├── api_client/
    │
    ├── endpoints/
    │   ├── base.py
    │   ├── noaa/
    │   │   ├── water_temperature.py
    │   │   ├── tides.py
    │   │   └── station.py
    │   │
    │   ├── ndbc/
    │   │   └── ...
    │   │
    │   └── openmeteo/
    │       └── ...
    │
    ├── models/
    │   ├── noaa/
    │   ├── ndbc/
    │   └── ...
    │
    └── services/

```

Notice:
`api_client/` becomes generic. `endpoints/` contain API-specific behavior.

---

### Level 1: ApiClient
Your client should only know:
- retries
- timeout
- SSL
- session handling


Example:

```python
class ApiClient:

    def get_json(
        self,
        url: str,
        params: dict[str, str] | None = None,
    ) -> dict:
        response = self.get(url, params=params)

        if response is None:
            raise ApiClientError("No response received")

        response.raise_for_status()

        return response.json()

```


No NOAA knowledge.
No tide knowledge.
No weather knowledge.

---

### Level 2: Base Endpoint

Create a common endpoint abstraction.

```python
class BaseEndpoint:
    """Base class for API endpoints."""

    BASE_URL: str

    def __init__(self, client: ApiClient):
        self.client = client

```

Then NOAA endpoints inherit.

---

### Level 3: NOAA API

Instead of scattered URL constants:

```python
NOAA_BASE_URL = (
    "https://api.tidesandcurrents.noaa.gov/api/prod"
)
```

Create:

```python
class NoaaApi:
    BASE_URL = (
        "https://api.tidesandcurrents.noaa.gov/api/prod"
    )

    def __init__(self, client: ApiClient):
        self.client = client

```

Then:

```python
class WaterTemperatureEndpoint(NoaaApi):

    PATH = "/datagetter"

    def get(
        self,
        params: NoaaWaterTempParams,
    ) -> NoaaWaterTempResponse:

        data = self.client.get_json(
            f"{self.BASE_URL}{self.PATH}",
            params=params.to_query_params(),
        )

        return NoaaWaterTempResponse.model_validate(data)

```

Usage:

```python
client = ApiClient()

water_temp = WaterTemperatureEndpoint(client)

result = water_temp.get(
    NoaaWaterTempParams(
        station="8534720"
    )
)

```

This scales extremely well.

---

## Dataclass vs Pydantic

For API contracts, I would use Pydantic.
Instead of:

```python
@dataclass
class NoaaWaterTempParams:

```

I'd use: 

```python
from pydantic import BaseModel

class NoaaWaterTempParams(BaseModel):
    station: str
    product: str = "water_temperature"
    application: str = "ocean-report"

```

Then:

```python
params.model_dump(
    by_alias=True,
    exclude_none=True,
)

```

Benefits:
Validation

```python
time_zone: str = Field(
    alias="time_zone"
)

```

### Constrains

```
station: str = Field(
    min_length=7,
    max_length=7,
)

```

**JSON serialization**
Already built in.

---

### Response Models
This is where Pydantic really shines.
Instead of:

```python
response.json()
```

everywhere:


```python
class WaterTemperatureDatum(BaseModel):
    t: str
    v: str

class NoaaWaterTempResponse(BaseModel):
    data: list[WaterTemperatureDatum]
```

Then:

```python
class WaterTemperatureDatum(BaseModel):
    t: str
    v: str

class NoaaWaterTempResponse(BaseModel):
    data: list[WaterTemperatureDatum]
```

Now the rest of your application never touches raw JSON.

## Error Handling

I would add custom exceptions immediately

```python
class ApiError(Exception):
    pass


class ApiConnectionError(ApiError):
    pass


class ApiResponseError(ApiError):
    pass


class ApiValidationError(ApiError):
    pass
```

Then your services can do:

```python
try:
    temp = endpoint.get(params)
except ApiError:
    ...

```

instead of checking:

```python
if response is None:

```

Returning None tends to create defensive code everywhere.
Raise exceptions instead.

---

## Dependcy Injection 

Pass the client into endpoints.

```python
client = ApiClient()

water_temp_endpoint = WaterTemperatureEndpoint(client)
tide_endpoint = TideEndpoint(client)
```

This makes testing easy.

```python
mock_client = Mock()
endpoint = WaterTemperatureEndpoint(mock_client)
```

---

## Long Term Design

If I were designing Ocean Report from scratch for a 5+ year lifespan, I'd structure it like this:

```
api_client/
│
├── client.py
├── exceptions.py
│
├── endpoints/
│   ├── noaa/
│   │   ├── water_temperature.py
│   │   ├── tides.py
│   │   └── stations.py
│   │
│   ├── ndbc/
│   └── openmeteo/
│
├── models/
│   ├── noaa/
│   ├── ndbc/
│   └── openmeteo/
│
└── services/
    ├── surf_report_service.py
    ├── tide_service.py
    └── email_service.py

```

The key rule:
>>Transport layer knows HTTP. Endpoints know URLs. Models know schemas. Services know business logic.
Keeping those four responsibilities separate is what will make the project remain intuitive when it grows from 3 endpoints to 30.
