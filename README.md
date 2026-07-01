# Lush Task Manager

## Requirements 

### Functional 
- CRUD Projects, tasks 
- Fetch single and list of tasks 
- Filtering
- Sorting
- Assignment / Unassignment
- Status updates

### Non-functional 
- Asynchronous queries
- Efficient resolution of tasks
- Authentication (even if stubbed)
- Runnability
- Data migrations (rollbacks too)
- Typed Errors (no straight 500s or leaked stacktraces)

## Feature Priorities
1. Project and Task lifecycle (create, link, assign, unassign, delete)
   1. Extra Considerations: concurrent access and updates
2. Read Tasks 
   1. Extra Considerations: pagination with scale
3. Data Loader / N + 1 prevention 
4. Typed errors
5. Filter/Sort (project, status, assignee, creation date)

## Design Decisions 

### Users 
- I Decided to leave out GraphQL and CRUD logic around users. This was done to focus on the project and task management. 
  - I believe it is simpler to add users via a script rather than adding additional logic, classes, and types to manage them 
  - likewise, as the assignment stands, user management is not required

### Optimistic Locking 
- Optimistic locking is a good approach to ensuring concurrent writes are not overwritten by each other. Using an incremental version instead of timestamps is both simpler, and it avoids server time drifts.
- If pessimistic locking were used, many users would not be able to efficiently view the same task as it would be locked on a read level. 
- Downstream, optimistic locking prevents deadlocks as the lock is not acquired at read level.

### Heavy integration testing 
- With the requirements of this application, there are not many components that have meaningful areas to unit test. More value comes from integration tests that can test the flow from request to datbase.

## Testing

### Limitations

An SQLlite in-memory database will be used instead of a TestContainer or actual instance of Postgres.
This has been done due to simplicity of testing with no containers needed to be spun up and the time limitations as this provides faster implementation and the extra features of postgres are not required for these testing purposes.