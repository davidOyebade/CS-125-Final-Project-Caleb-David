# API Usage Examples

## Event Types Endpoints

### 1. GET all event types
Retrieves all event types with their custom field schemas.

**Request:**
```bash
curl -X GET "http://127.0.0.1:8000/event-types"
```

**Or in a browser:**
```
http://127.0.0.1:8000/event-types
```

---

### 2. GET a specific event type by ID
Retrieves a specific event type schema.

**Request:**
```bash
curl -X GET "http://127.0.0.1:8000/event-types/1"
```

**Or in a browser:**
```
http://127.0.0.1:8000/event-types/1
```

---

### 3. POST a new event type
Creates a new event type with custom fields.

**Request:**
```bash
curl -X POST "http://127.0.0.1:8000/event-types" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Lock-In",
    "custom_fields": [
      {
        "field_name": "overnight",
        "data_type": "boolean"
      },
      {
        "field_name": "permission_slip_required",
        "data_type": "boolean"
      },
      {
        "field_name": "max_participants",
        "data_type": "number"
      }
    ]
  }'
```

**Using Python requests:**
```python
import requests

url = "http://127.0.0.1:8000/event-types"
payload = {
    "name": "Lock-In",
    "custom_fields": [
        {
            "field_name": "overnight",
            "data_type": "boolean"
        },
        {
            "field_name": "permission_slip_required",
            "data_type": "boolean"
        },
        {
            "field_name": "max_participants",
            "data_type": "number"
        }
    ]
}

response = requests.post(url, json=payload)
print(response.json())
```

**Using JavaScript (fetch):**
```javascript
fetch('http://127.0.0.1:8000/event-types', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
  },
  body: JSON.stringify({
    name: "Lock-In",
    custom_fields: [
      {
        field_name: "overnight",
        data_type: "boolean"
      },
      {
        field_name: "permission_slip_required",
        data_type: "boolean"
      },
      {
        field_name: "max_participants",
        data_type: "number"
      }
    ]
  })
})
.then(response => response.json())
.then(data => console.log(data));
```

---

## Events Endpoints

### 4. GET event with custom data
Retrieves an event with its custom field values.

**Request:**
```bash
curl -X GET "http://127.0.0.1:8000/events/1"
```

---

### 5. POST create event with custom data
Creates a new event and stores custom field values.

**Request:**
```bash
curl -X POST "http://127.0.0.1:8000/events" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Winter Lock-In 2025",
    "event_type_id": 6,
    "place_id": 2,
    "start_date_time": "2025-12-20 18:00:00",
    "end_date_time": "2025-12-21 10:00:00",
    "custom_field_values": {
      "overnight": true,
      "permission_slip_required": true,
      "max_participants": 50
    }
  }'
```

---

### 6. PUT update event custom data
Updates the custom field values for an existing event.

**Request:**
```bash
curl -X PUT "http://127.0.0.1:8000/events/3/custom-data" \
  -H "Content-Type: application/json" \
  -d '{
    "custom_field_values": {
      "packing_list": "Updated packing list: sleeping bag, pillow, toiletries, Bible, notebook, warm clothes, flashlight, extra snacks",
      "bring_friend": true,
      "accommodation_type": "Cabin with bunk beds",
      "cost_per_person": 85,
      "meals_included": true
    }
  }'
```

**Using Python requests:**
```python
import requests

url = "http://127.0.0.1:8000/events/3/custom-data"
payload = {
    "custom_field_values": {
        "packing_list": "Updated packing list: sleeping bag, pillow, toiletries",
        "bring_friend": True,
        "accommodation_type": "Cabin with bunk beds",
        "cost_per_person": 85,
        "meals_included": True
    }
}

response = requests.put(url, json=payload)
print(response.json())
```

**Note:** This endpoint will:
- Validate that the event exists
- Validate that all custom fields match the event type schema
- Validate data types (text, number, boolean)
- Update existing custom data or create it if it doesn't exist

---

## Redis Check-In Endpoints

### 7. POST check in a student
```bash
curl -X POST "http://127.0.0.1:8000/events/1/check-in/1"
```

### 8. POST check out a student
```bash
curl -X POST "http://127.0.0.1:8000/events/1/check-out/1"
```

### 9. GET all checked-in students
```bash
curl -X GET "http://127.0.0.1:8000/events/1/checked-in"
```

### 10. GET check-in count
```bash
curl -X GET "http://127.0.0.1:8000/events/1/check-in-count"
```

### 11. POST finalize event (persist to MySQL and cleanup Redis)
```bash
curl -X POST "http://127.0.0.1:8000/events/1/finalize"
```

---

## Key Points

- **GET requests** are for retrieving data (no body needed)
- **POST requests** are for creating data (require a JSON body)
- The HTTP method (GET, POST, PUT, DELETE) determines which endpoint function runs
- FastAPI automatically generates interactive docs at `/docs` where you can test all endpoints

