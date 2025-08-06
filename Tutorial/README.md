
---

# 📘 Quick Guide: Creating Environments, Accounts, and Using Replay

### 🔑 Core model

The system is structured around a **Trader → Environment → FIX Account** hierarchy:

* **Trader**: The root entity that owns all environments and accounts.

  > For now, everything is managed under a single default trader:
  > `username = plutus`, `password = 123`

* **Environment (Env)**: A sandbox for trading or replaying data.

  * One trader can create multiple environments.
  * Each environment has a mode:

    * `realtime-kafka` → real-time simulation **matched with live market prices**
    * `replay-postgres` → playback of historical market data

* **FIX Account**: Accounts inside an environment.

  * One environment can contain multiple FIX accounts.
  * FIX accounts are used by clients (bots, users) to connect and trade.

ℹ️ **Tip:** You can try all APIs directly in **Swagger UI** (usually at `/swagger-ui.html` or `/swagger-ui/index.html`) without needing to craft raw HTTP requests.

---

### 🏗️ Step 1: Create an Environment

**Endpoint:** `POST /api/environment/create`

**Parameters:**

* `username` = `plutus` *(default)*
* `password` = `123` *(default)*
* `mode` = `realtime-kafka` *(live market)* or `replay-postgres` *(historical playback)*
* `customEnvID` (optional)

**Example:**

```http
POST /api/environment/create?username=plutus&password=123&mode=replay-postgres
```

**Response:**

```json
{
  "success": true,
  "env_id": "plutu-r12345",
  "mode": "replay-postgres"
}
```

---

### 🏦 Step 2: Create a FIX Account

**Endpoint:** `POST /api/account/create`

**Parameters:**

* `traderUsername` = `plutus` *(default)*
* `traderPassword` = `123` *(default)*
* `envID` = ID of the environment you created
* `fixAccountUsername` = account login name
* `fixAccountPassword` = account login password
* `initialBalance` (optional, default = `1,000,000,000,000`)

**Defaults for fees & margins:**

* Stock fees = `0`
* Stock margin ratio = `1.0`
* Derivative margin ratio = `0.25`
* Derivative fee = `20,000` per contract (pct = 0)
* Unlimited balance = `false`

**Example:**

```http
POST /api/account/create?envID=plutu-r12345&fixAccountUsername=bot1&fixAccountPassword=123
```

**Response:**

```json
{
  "success": true,
  "account_id": "a1b2c3d4",
  "env_id": "plutu-r12345",
  "initial_balance": 1000000000000
}
```

---

### 🎬 Step 3: Configure and Start Replay (for replay environments)

Replay environments allow you to **play back a pre-defined set of market symbols** stored on the server.
Clients do not need to specify symbols — they are pre-configured in the system.

#### 3.1 Configure Replay Parameters

**Endpoint:** `POST /api/replay-quote/envinfo`

**Body:**

```json
{
  "envID": "plutu-r12345",
  "start": "2025-01-01",
  "end": "2025-07-28",
  "speedFactor": 3
}
```

**Notes:**

* **Date format** must be `yyyy-MM-dd` (ISO).
* **Speed factor**:

  * `1` → real-time playback
  * `3` → 3× faster (1 second real time = 3 seconds of market data)
  * `<1` → slower than real time
* Replay runs **continuously across sessions and trading days** with no long pauses.
  Minor delays may occur while loading data.
* All of this can be tested conveniently using **Swagger UI**.

---

#### 3.2 Start Replay

**Endpoint:** `POST /api/replay-quote/start`

**Body:**

```json
{
  "envID": "plutu-r12345"
}
```

**Response:**

```json
{
  "success": true
}
```

---

✅ With these three steps, you can set up:

1. An **environment** for testing.
2. One or more **FIX accounts** under that environment.
3. Run **replay playback** to simulate historical market data,
   or use **`realtime-kafka` mode to match orders against live market prices**.

💡 For quick testing and exploration, use **Swagger UI** instead of Postman/curl. It provides an interactive interface to fill in parameters and send requests immediately.

---

