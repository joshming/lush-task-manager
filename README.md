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
- This was not implemented on projects despite mutation availability. Although a project can only be edited by the creator, there is the chance that concurrent requests go off. To prevent another migration script and for time constraints, I have omitted this feature. 

### Heavy integration testing 
- With the requirements of this application, there are not many components that have meaningful areas to unit test. More value comes from integration tests that can test the flow from request to datbase.

### Unique Title + project_id / created_by for tasks / projects
- It makes sense that for a given project, there could be multiple projects with the same title but different users (each could have a project for their own)
  - It doesn't make sense for a user to have multiple projects with the same name
  - A project should be re-opened if a user needs the same one 
- For a given project, multiple tasks with the same name doesn't make sense, instead they should be unique within a project
- A functional index would have been ideal to get rid of the necessity of a "normalized" title field that's been set to lower case. However, due to SQLite testing set up and time limitations, normalized_title short-cut was taken instead

### Rate Limiter Bonus 
#### "Authorized" user based limiting
- Assumption is that the user is always presenting this header and always authorized, therefore, this is more accurate than an IP, which can be spoofed with different VM's with different public IPs
- trade off: if unauthorized users without the header were allowed to make a request, than the rate limiting would be ineffective 
  - anonymous requests default to ip
  
#### Reason for implementation
- I was watching system design videos and coincidentally came across a GraphQL vs REST video. A specific point was that a rate limiter is non-trivial in a graphql service due to a singular endpoint
  - this made complete sense, and sparked interest and I wanted to implement one for my own learning
- In general though, a rate limiter is a key component to any user-facing service, preventing popular DDoS attacks and intense pressure on database
- I limited mutations more than queries as typically, a write does consume more resources, but the amounts were arbitrary. Realistically, these limits would be chosen off of the systems capabilities / resources. 

#### Trade off
- In memory storage: for the sake of this assignment. Would be better with a redis cache or something equivalent to prevent loss of data on restart
- General limits for mutations: different types of mutations would consume different amount of resources. In this exercise, I treated them all as the same

## Testing

### Limitations

#### SQLite
An SQLlite in-memory database will be used instead of a TestContainer or actual instance of Postgres.
This has been done due to simplicity of testing with no containers needed to be spun up and the time limitations as this provides faster implementation and the extra features of postgres are not required for these testing purposes.

Integrity error tests have been omitted. This is because SQLite raises different exception types. I could test via sql state however, that seems more unclear than catching the postgres database exceptions from the postgres driver.

Testing for similar cases (e.g. sorting by Status vs Priority or ID vs Project_ID) were omitted for time. In a real-world I'd implement them, however, to save on time, I omitted them as they logically follow the same rules 