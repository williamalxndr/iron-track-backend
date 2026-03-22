# IronTrack API Documentation

## Overview

**Base URL:** `/api/v1/`

IronTrack backend provides a RESTful API for workout tracking, exercise management, and plan management. Designed for offline-first mobile sync.

### Authentication

> **Future feature.** Currently all endpoints are public (`AllowAny`).
>
> When implemented: `Authorization: Bearer <token>`

### Response Format

**Success:**

```json
{
  "data": { ... },
  "message": "success"
}
```

**Error:**

```json
{
  "error": {
    "code": "INVALID_REQUEST",
    "message": "Description of what went wrong"
  }
}
```

### Common Status Codes

| Code | Meaning |
|------|---------|
| 200  | OK — successful GET |
| 201  | Created — successful POST |
| 400  | Bad Request — invalid payload |
| 404  | Not Found — resource doesn't exist |
| 500  | Internal Server Error |

### Key Rules

- **No derived fields in responses.** Volume, PR, and progression are always computed client-side from `weight` and `reps`.
- **IDs are integers** (future: UUID for offline-safe sync).
- **Timestamps** use ISO 8601 format: `2026-03-22T10:00:00Z`
- **Dates** use `YYYY-MM-DD` format: `2026-03-22`

---

## 1. Exercise

### GET /exercises/

List all exercises.

**Response** `200 OK`

```json
{
  "data": [
    {
      "id": 1,
      "name": "Bench Press",
      "category": "Push",
      "created_at": "2026-03-22T10:00:00Z"
    },
    {
      "id": 2,
      "name": "Squat",
      "category": "Legs",
      "created_at": "2026-03-22T10:00:00Z"
    }
  ],
  "message": "success"
}
```

| Field | Type | Description |
|-------|------|-------------|
| `id` | integer | Exercise ID |
| `name` | string | Exercise name |
| `category` | string \| null | Category (e.g., Push, Pull, Legs) |
| `created_at` | datetime | When the exercise was created |

---

### GET /exercises/{id}/history/

Get all past logs for a specific exercise, grouped by session date, ordered descending.

**Path Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `id` | integer | Yes | Exercise ID |

**Response** `200 OK`

```json
{
  "data": [
    {
      "date": "2026-03-22",
      "sets": [
        { "weight": 80.0, "reps": 8 },
        { "weight": 80.0, "reps": 6 },
        { "weight": 75.0, "reps": 8 }
      ]
    },
    {
      "date": "2026-03-20",
      "sets": [
        { "weight": 77.5, "reps": 8 },
        { "weight": 77.5, "reps": 7 }
      ]
    }
  ],
  "message": "success"
}
```

| Field | Type | Description |
|-------|------|-------------|
| `date` | date | Session date |
| `sets` | array | Sets performed on that date |
| `sets[].weight` | float | Weight in kg |
| `sets[].reps` | integer | Number of repetitions |

**Response** `404 Not Found` — exercise does not exist

---

### GET /exercises/{id}/stats/

Get personal record (PR) stats for a specific exercise. All values are computed, never stored.

**Path Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `id` | integer | Yes | Exercise ID |

**Response** `200 OK`

```json
{
  "data": {
    "max_weight": 100.0,
    "max_reps": 12,
    "max_volume": 800.0
  },
  "message": "success"
}
```

| Field | Type | Description |
|-------|------|-------------|
| `max_weight` | float | Highest weight ever lifted for this exercise |
| `max_reps` | integer | Highest reps in a single set for this exercise |
| `max_volume` | float | Highest single-set volume (`weight * reps`) |

**Note:** If exercise has no logged sets, returns `{"max_weight": 0, "max_reps": 0, "max_volume": 0}`.

**Response** `404 Not Found` — exercise does not exist

---

## 2. Workout Session

### GET /sessions/

List all workout sessions, ordered by date descending.

**Response** `200 OK`

```json
{
  "data": [
    {
      "id": 1,
      "date": "2026-03-22",
      "notes": "Felt strong today",
      "created_at": "2026-03-22T10:00:00Z"
    },
    {
      "id": 2,
      "date": "2026-03-20",
      "notes": null,
      "created_at": "2026-03-20T09:30:00Z"
    }
  ],
  "message": "success"
}
```

| Field | Type | Description |
|-------|------|-------------|
| `id` | integer | Session ID |
| `date` | date | Workout date |
| `notes` | string \| null | Optional session notes |
| `created_at` | datetime | When the session was created |

---

### POST /sessions/

Create a new workout session with exercises and sets.

**Request Body:**

```json
{
  "date": "2026-03-22",
  "notes": "Push day",
  "exercises": [
    {
      "exercise_id": 1,
      "sets": [
        { "weight": 80.0, "reps": 8 },
        { "weight": 80.0, "reps": 6 }
      ]
    },
    {
      "exercise_id": 3,
      "sets": [
        { "weight": 40.0, "reps": 10 },
        { "weight": 40.0, "reps": 10 },
        { "weight": 40.0, "reps": 8 }
      ]
    }
  ]
}
```

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `date` | date | Yes | Workout date (`YYYY-MM-DD`) |
| `notes` | string | No | Session notes |
| `exercises` | array | Yes | List of exercises performed |
| `exercises[].exercise_id` | integer | Yes | Reference to exercise |
| `exercises[].sets` | array | Yes | Sets for this exercise |
| `exercises[].sets[].weight` | float | Yes | Weight in kg |
| `exercises[].sets[].reps` | integer | Yes | Number of repetitions |

**Response** `201 Created`

```json
{
  "data": {
    "id": 1
  },
  "message": "success"
}
```

**Response** `400 Bad Request`

```json
{
  "error": {
    "code": "INVALID_REQUEST",
    "message": "date is required"
  }
}
```

---

### GET /sessions/{id}/

Get session detail with all exercises and sets.

**Path Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `id` | integer | Yes | Session ID |

**Response** `200 OK`

```json
{
  "data": {
    "id": 1,
    "date": "2026-03-22",
    "notes": "Push day",
    "exercises": [
      {
        "exercise_id": 1,
        "exercise_name": "Bench Press",
        "sets": [
          { "weight": 80.0, "reps": 8 },
          { "weight": 80.0, "reps": 6 }
        ]
      },
      {
        "exercise_id": 3,
        "exercise_name": "Overhead Press",
        "sets": [
          { "weight": 40.0, "reps": 10 },
          { "weight": 40.0, "reps": 10 },
          { "weight": 40.0, "reps": 8 }
        ]
      }
    ]
  },
  "message": "success"
}
```

| Field | Type | Description |
|-------|------|-------------|
| `id` | integer | Session ID |
| `date` | date | Workout date |
| `notes` | string \| null | Session notes |
| `exercises` | array | Exercises in order |
| `exercises[].exercise_id` | integer | Exercise ID |
| `exercises[].exercise_name` | string | Exercise name |
| `exercises[].sets` | array | Sets in order |
| `exercises[].sets[].weight` | float | Weight in kg |
| `exercises[].sets[].reps` | integer | Reps |

**Response** `404 Not Found` — session does not exist

---

## 3. Plan

### GET /plans/

List all workout plans.

**Response** `200 OK`

```json
{
  "data": [
    {
      "id": 1,
      "name": "Push Day",
      "type": "PUSH"
    },
    {
      "id": 2,
      "name": "Pull Day",
      "type": "PULL"
    }
  ],
  "message": "success"
}
```

| Field | Type | Description |
|-------|------|-------------|
| `id` | integer | Plan ID |
| `name` | string | Plan name |
| `type` | string | Plan type: `PUSH`, `PULL`, `LEG`, `FULL_BODY` |

---

### POST /plans/

Create a new workout plan with exercises.

**Request Body:**

```json
{
  "name": "Push Day",
  "type": "PUSH",
  "exercises": [
    {
      "exercise_id": 1,
      "target_sets": 3,
      "target_reps": 10
    },
    {
      "exercise_id": 3,
      "target_sets": 3,
      "target_reps": 8
    }
  ]
}
```

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `name` | string | Yes | Plan name |
| `type` | string | Yes | Plan type (`PUSH`, `PULL`, `LEG`, `FULL_BODY`) |
| `exercises` | array | No | Exercises in the plan |
| `exercises[].exercise_id` | integer | Yes | Reference to exercise |
| `exercises[].target_sets` | integer | No | Target number of sets |
| `exercises[].target_reps` | integer | No | Target number of reps |

**Response** `201 Created`

```json
{
  "data": {
    "id": 1
  },
  "message": "success"
}
```

**Response** `400 Bad Request`

```json
{
  "error": {
    "code": "INVALID_REQUEST",
    "message": "name is required"
  }
}
```

---

### GET /plans/{id}/

Get plan detail with exercises and targets.

**Path Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `id` | integer | Yes | Plan ID |

**Response** `200 OK`

```json
{
  "data": {
    "id": 1,
    "name": "Push Day",
    "type": "PUSH",
    "exercises": [
      {
        "exercise_id": 1,
        "exercise_name": "Bench Press",
        "target_sets": 3,
        "target_reps": 10
      },
      {
        "exercise_id": 3,
        "exercise_name": "Overhead Press",
        "target_sets": 3,
        "target_reps": 8
      }
    ]
  },
  "message": "success"
}
```

| Field | Type | Description |
|-------|------|-------------|
| `id` | integer | Plan ID |
| `name` | string | Plan name |
| `type` | string | Plan type |
| `exercises` | array | Exercises in order |
| `exercises[].exercise_id` | integer | Exercise ID |
| `exercises[].exercise_name` | string | Exercise name |
| `exercises[].target_sets` | integer \| null | Target sets |
| `exercises[].target_reps` | integer \| null | Target reps |

**Response** `404 Not Found` — plan does not exist

---

## 4. Plan Weekly

### GET /plan-weekly/

List all weekly plans.

**Response** `200 OK`

```json
{
  "data": [
    {
      "id": 1,
      "name": "PPL Split"
    },
    {
      "id": 2,
      "name": "Upper Lower"
    }
  ],
  "message": "success"
}
```

| Field | Type | Description |
|-------|------|-------------|
| `id` | integer | Weekly plan ID |
| `name` | string | Weekly plan name |

---

### GET /plan-weekly/{id}/

Get weekly plan detail with day-plan assignments.

**Path Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `id` | integer | Yes | Weekly plan ID |

**Response** `200 OK`

```json
{
  "data": {
    "id": 1,
    "name": "PPL Split",
    "items": [
      {
        "day_of_week": 1,
        "plan_id": 1,
        "plan_name": "Push Day"
      },
      {
        "day_of_week": 2,
        "plan_id": 2,
        "plan_name": "Pull Day"
      },
      {
        "day_of_week": 3,
        "plan_id": 3,
        "plan_name": "Leg Day"
      },
      {
        "day_of_week": 4,
        "plan_id": 1,
        "plan_name": "Push Day"
      },
      {
        "day_of_week": 5,
        "plan_id": 2,
        "plan_name": "Pull Day"
      }
    ]
  },
  "message": "success"
}
```

| Field | Type | Description |
|-------|------|-------------|
| `id` | integer | Weekly plan ID |
| `name` | string | Weekly plan name |
| `items` | array | Day-plan assignments |
| `items[].day_of_week` | integer | Day of week (1=Monday, 7=Sunday) |
| `items[].plan_id` | integer | Plan ID assigned to this day |
| `items[].plan_name` | string | Plan name |

**Response** `404 Not Found` — weekly plan does not exist

---

## 5. Sync (Future)

> These endpoints are planned but **not yet implemented**. Documented here for reference.

### POST /sync/batch/

Send a batch of local operations to the server.

**Request Body:**

```json
{
  "device_id": "uuid",
  "operations": [
    {
      "op_id": "uuid",
      "entity": "WorkoutSession",
      "action": "create",
      "data": {
        "id": "uuid",
        "date": "2026-03-22",
        "notes": ""
      },
      "timestamp": "2026-03-22T10:00:00Z"
    }
  ]
}
```

**Response** `200 OK`

```json
{
  "data": {
    "acknowledged": ["op_id_1", "op_id_2"],
    "failed": []
  },
  "message": "success"
}
```

**Rules:**
- Each operation must have a unique `op_id`
- Duplicate `op_id`s are silently ignored (idempotent)
- Supported entities: `WorkoutSession`, `Exercise`, `ExerciseLog`, `SetLog`, `Plan`, `PlanExercise`, `PlanWeekly`, `PlanWeeklyItem`
- Supported actions: `create`, `update`, `delete`

---

### GET /sync/changes/?since=timestamp

Get all changes since a given timestamp.

**Query Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `since` | datetime | Yes | ISO 8601 timestamp |

**Response** `200 OK`

```json
{
  "data": {
    "changes": [
      {
        "entity": "WorkoutSession",
        "action": "create",
        "data": {
          "id": "uuid",
          "date": "2026-03-22"
        }
      }
    ],
    "server_time": "2026-03-22T12:00:00Z"
  },
  "message": "success"
}
```

---

## Endpoint Summary

| Method | Endpoint | Description | Status |
|--------|----------|-------------|--------|
| GET | `/exercises/` | List exercises | Planned |
| GET | `/exercises/{id}/history/` | Exercise history | Planned |
| GET | `/exercises/{id}/stats/` | Exercise PR stats | Planned |
| GET | `/sessions/` | List sessions | Planned |
| POST | `/sessions/` | Create session | Planned |
| GET | `/sessions/{id}/` | Session detail | Planned |
| GET | `/plans/` | List plans | Planned |
| POST | `/plans/` | Create plan | Planned |
| GET | `/plans/{id}/` | Plan detail | Planned |
| GET | `/plan-weekly/` | List weekly plans | Planned |
| GET | `/plan-weekly/{id}/` | Weekly plan detail | Planned |
| POST | `/sync/batch/` | Batch sync | Future |
| GET | `/sync/changes/` | Get changes | Future |
