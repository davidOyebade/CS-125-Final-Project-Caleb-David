# Youth Group Management System

**By:** Caleb Song and David Oyebade  
**Team Name:** Rush Hour  
**Course:** CS-125 Database Design  
**Professor:** Mike Ryu

---

## Product Requirements

### Who is using this?
Pastors/Youth leaders

### What do they want to do?

#### Manage People
- Keep track of students, parents/guardians, leaders, and volunteers
  - Parent-student relationship
  - Leader/volunteer availability and scheduling
- Manage small groups and determine who is in which group
  - Keep track of meetings and take notes
- Store personal information for each person
  - Contact info
  - Prayer requests/updates
  - Track attendance

#### Manage Events
- Master calendar to organize upcoming and past events
  - See who is attending, who is working
    - Register students for events and record attendance
  - Take notes on events
  - Get live updates of who is there and who isn't
    - Track sign-ins and sign-outs

### What should and shouldn't they be able to do?

#### What they should be able to do
- **Note-taking**
  - Look up notes from past events
  - Enter in notes for new events
- **Attendance information**
  - View current and past attendance information
- **Student information**
  - View student instances with relevant information
    - Parents
    - Address
    - Etc.

#### What they shouldn't be able to do
- Edit information of other people without being the admin/head pastor
- Add contradictory information
  - Future birthdate
  - Scheduling to be in two places at once
- Invalid check-ins
  - Check people in/out when an event is not in progress
  - Check in a person at two places at once

---

## Implementing the API

### Required Software

1. **MySQL 9.5**
2. **Python 3.10**

Use the following command to start MySQL on Ubuntu:
```bash
sudo service start mysql
```

### Required Account Instances

1. **MongoDB**
2. **Redis**

### Creating Your Database

1. Run both the `yg_create_tables.sql` and `yg_data_insert.sql` files in order.
2. Add the `FP_YG_app` database to MySQL using the following commands in Ubuntu:
   ```bash
   mysql -u root -p FP_YG_app < yg_create_tables.sql
   mysql -u root -p FP_YG_app < yg_data_insert.sql
   ```

### Initializing MongoDB and Redis

#### 1. MongoDB

1. Go to [https://www.mongodb.com/](https://www.mongodb.com/) and create an account. **Make sure to save your login credentials** because you will need them.
2. Once you are logged in, create a project and name it something that refers to the youth group API.
3. Create a cluster within that project using MongoDB's free tier, and name it.
4. Create a database user, and **be sure to save your credentials** because you will need them.
5. Choose a connection method and select **Drivers**.
6. Copy the connection string and add it to your `env` file and save it as `MONGO_URI`.
7. Run `mongodb_implement.py`.

#### 2. Redis

1. Go to [https://redis.io/try-free/](https://redis.io/try-free/) and create an account. **Make sure to save your credentials**.
2. Create a new database and select their free model.
3. Name your database and leave all other settings as is.
4. Under the configuration tab, select **"Connect using Redis CLI, Client, or Insight"**.
5. Select **Redis Client** and then within Redis client select **Python**.
6. You will be presented a code snippet. From that code snippet, copy the following two pieces of information:
   - Copy the Redis host and store it in your `env` file and name it `redis_host` (exclude quotation marks when you store in env).
   - Copy your password and store it in your `env` file and name it `redis_password` (exclude quotation marks when you store in env).
7. Run `redis_implement.py`.

### Running the API

1. Run the following installs for required packages using the command:
   ```bash
   pip install pydantic fastapi uvicorn mysql-connector-python
   ```
   Or install all dependencies from `requirements.txt`:
   ```bash
   pip install -r requirements.txt
   ```

2. Update the database configurations to match your system in the `main.py` file.

3. Run the `main.py` program to check for a successful connection.

4. Run the following command to create your API:
   ```bash
   uvicorn main:app --reload --port 8000
   ```

5. Use the link [http://127.0.0.1:8000/](http://127.0.0.1:8000/) to access the API.

6. Use the endpoints to execute queries! See the `InsomniaSS.png` for an example.

---

## Important Notes

⚠️ **ALL DATA IS GENERATED AND NOT REAL. ALL PASSWORDS IN THE REPOSITORY ARE OUT OF DATE AND NO LONGER VALID.**

