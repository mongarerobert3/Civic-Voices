# To-Do List REST API

This project is a **To-Do List REST API** built using **Node.js**, **Express**, and **MongoDB**. It includes features such as user authentication and task management.

---

## Features

1. **User Authentication:**
   - Register a new user.
   - Login with email and password.
   - JWT-based authentication for secure API access.

2. **Task Management:**
   - Create tasks.
   - Retrieve all tasks for the logged-in user.
   - Update tasks by ID.
   - Delete tasks by ID.

3. **Middleware:**
   - Verify JWT for protected routes.

4. **Database:**
   - MongoDB for data persistence.
   - Mongoose for schema definition and data modeling.

---

## Installation

1. Clone the repository:
   ```bash
   git clone <repository-url>
   ```

2. Navigate to the project directory:
   ```bash
   cd todo-list-api
   ```

3. Install dependencies:
   ```bash
   npm install
   ```

4. Create a `.env` file in the root directory and add the following variables:
   ```env
   PORT=3000
   MONGO_URI=<your-mongodb-uri>
   JWT_SECRET=<your-secret-key>
   ```

5. Start the server:
   ```bash
   npm start
   ```

6. The API will run on `http://localhost:3000` by default.

---

## API Endpoints

### **Authentication**

#### Register
- **POST** `/api/auth/register`
- **Description:** Register a new user.
- **Request Body:**
  ```json
  {
    "name": "John Doe",
    "email": "johndoe@example.com",
    "password": "password123"
  }
  ```
- **Response:**
  ```json
  {
    "token": "<jwt-token>"
  }
  ```

#### Login
- **POST** `/api/auth/login`
- **Description:** Login an existing user.
- **Request Body:**
  ```json
  {
    "email": "johndoe@example.com",
    "password": "password123"
  }
  ```
- **Response:**
  ```json
  {
    "token": "<jwt-token>"
  }
  ```

### **Tasks**

#### Create a Task
- **POST** `/api/tasks`
- **Protected:** Yes (requires JWT in `Authorization` header).
- **Request Body:**
  ```json
  {
    "text": "Complete project documentation",
    "completed": false
  }
  ```
- **Response:**
  ```json
  {
    "_id": "<task-id>",
    "userId": "<user-id>",
    "text": "Complete project documentation",
    "completed": false
  }
  ```

#### Get All Tasks
- **GET** `/api/tasks`
- **Protected:** Yes.
- **Response:**
  ```json
  [
    {
      "_id": "<task-id>",
      "userId": "<user-id>",
      "text": "Complete project documentation",
      "completed": false
    }
  ]
  ```

#### Update a Task
- **PUT** `/api/tasks/:id`
- **Protected:** Yes.
- **Request Body:**
  ```json
  {
    "text": "Update API documentation",
    "completed": true
  }
  ```
- **Response:**
  ```json
  {
    "_id": "<task-id>",
    "userId": "<user-id>",
    "text": "Update API documentation",
    "completed": true
  }
  ```

#### Delete a Task
- **DELETE** `/api/tasks/:id`
- **Protected:** Yes.
- **Response:**
  ```json
  {
    "message": "Task deleted successfully."
  }
  ```

---


## Dependencies

- **express:** Web framework for Node.js.
- **mongoose:** MongoDB object modeling tool.
- **jsonwebtoken:** For generating and verifying JWT tokens.
- **bcryptjs:** For hashing user passwords.
- **dotenv:** For environment variable management.

---

## Notes

- Ensure `MONGO_URI` is properly set in the `.env` file for MongoDB connection.
- Use secure values for `JWT_SECRET` to prevent unauthorized access.

---

## License
Feel free to use, modify, and distribute it as needed.

