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

## Feature Priorities
1. Project and Task lifecycle (create, link, assign, unassign, delete)
   1. Extra Considerations: concurrent access and updates
2. Read Tasks 
   1. Extra Considerations: pagination with scale
3. Data Loader / N + 1 prevention 
4. Typed errors
5. Filter/Sort (project, status, assignee, creation date)
