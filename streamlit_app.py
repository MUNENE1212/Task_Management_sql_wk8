import streamlit as st
import requests
import pandas as pd
from datetime import datetime, date
import json

# Configuration
API_BASE_URL = "http://localhost:8001"

# Set page config
st.set_page_config(
    page_title="Task Management System",
    page_icon="📋",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 3rem;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 0.5rem 0;
    }
    .status-pending {
        color: #ff9800;
    }
    .status-in_progress {
        color: #2196f3;
    }
    .status-completed {
        color: #4caf50;
    }
    .priority-high {
        color: #f44336;
    }
    .priority-medium {
        color: #ff9800;
    }
    .priority-low {
        color: #4caf50;
    }
</style>
""", unsafe_allow_html=True)

# Helper functions
def make_request(method, endpoint, data=None, params=None):
    """Make HTTP request to the API"""
    url = f"{API_BASE_URL}{endpoint}"
    try:
        if method == "GET":
            response = requests.get(url, params=params)
        elif method == "POST":
            response = requests.post(url, json=data)
        elif method == "PUT":
            response = requests.put(url, json=data)
        elif method == "DELETE":
            response = requests.delete(url)

        if response.status_code in [200, 201]:
            return response.json(), None
        else:
            return None, f"Error {response.status_code}: {response.text}"
    except requests.exceptions.ConnectionError:
        return None, "Cannot connect to API. Make sure the FastAPI server is running on port 8001."
    except Exception as e:
        return None, f"Error: {str(e)}"

def get_users():
    """Get all users"""
    data, error = make_request("GET", "/users/")
    return data if data else []

def get_tasks(status=None, priority=None, owner_id=None):
    """Get tasks with optional filters"""
    params = {}
    if status:
        params["status"] = status
    if priority:
        params["priority"] = priority
    if owner_id:
        params["owner_id"] = owner_id

    data, error = make_request("GET", "/tasks/", params=params)
    return data if data else []

def get_stats():
    """Get dashboard statistics"""
    data, error = make_request("GET", "/stats")
    return data if data else {}

# Sidebar navigation
st.sidebar.title("📋 Task Management")
page = st.sidebar.selectbox(
    "Navigate to:",
    ["Dashboard", "Users", "Tasks", "Add User", "Add Task"]
)

# Main content based on selected page
if page == "Dashboard":
    st.markdown('<h1 class="main-header">📊 Dashboard</h1>', unsafe_allow_html=True)

    # Get statistics
    stats = get_stats()

    if stats:
        # Display metrics in columns
        col1, col2, col3, col4 = st.columns(4)

        with col1:
            st.metric("Total Users", stats.get("total_users", 0))
        with col2:
            st.metric("Total Tasks", stats.get("total_tasks", 0))
        with col3:
            st.metric("Pending Tasks", stats.get("pending_tasks", 0))
        with col4:
            st.metric("Completed Tasks", stats.get("completed_tasks", 0))

    st.markdown("---")

    # Recent tasks overview
    st.subheader("📝 Recent Tasks Overview")

    tasks = get_tasks()
    if tasks:
        # Convert to DataFrame for better display
        df_tasks = pd.DataFrame(tasks)

        # Format datetime columns
        if 'created_at' in df_tasks.columns:
            df_tasks['created_at'] = pd.to_datetime(df_tasks['created_at']).dt.strftime('%Y-%m-%d %H:%M')
        if 'updated_at' in df_tasks.columns:
            df_tasks['updated_at'] = pd.to_datetime(df_tasks['updated_at']).dt.strftime('%Y-%m-%d %H:%M')

        # Select relevant columns
        display_columns = ['id', 'title', 'status', 'priority', 'created_at']
        if all(col in df_tasks.columns for col in display_columns):
            st.dataframe(df_tasks[display_columns].tail(10), use_container_width=True)
        else:
            st.dataframe(df_tasks, use_container_width=True)
    else:
        st.info("No tasks found.")

elif page == "Users":
    st.markdown('<h1 class="main-header">👥 Users Management</h1>', unsafe_allow_html=True)

    users = get_users()

    if users:
        st.subheader(f"Total Users: {len(users)}")

        # Display users in a table
        df_users = pd.DataFrame(users)
        if 'created_at' in df_users.columns:
            df_users['created_at'] = pd.to_datetime(df_users['created_at']).dt.strftime('%Y-%m-%d %H:%M')

        st.dataframe(df_users, use_container_width=True)

        # User actions
        st.subheader("User Actions")
        col1, col2 = st.columns(2)

        with col1:
            selected_user_id = st.selectbox("Select User for Tasks",
                                          options=[user['id'] for user in users],
                                          format_func=lambda x: f"{x} - {next(u['username'] for u in users if u['id'] == x)}")

            if st.button("View User Tasks"):
                user_tasks = get_tasks(owner_id=selected_user_id)
                if user_tasks:
                    st.write(f"Tasks for User ID {selected_user_id}:")
                    df_user_tasks = pd.DataFrame(user_tasks)
                    st.dataframe(df_user_tasks, use_container_width=True)
                else:
                    st.info("No tasks found for this user.")

        with col2:
            delete_user_id = st.selectbox("Select User to Delete",
                                        options=[user['id'] for user in users],
                                        format_func=lambda x: f"{x} - {next(u['username'] for u in users if u['id'] == x)}")

            if st.button("Delete User", type="primary"):
                result, error = make_request("DELETE", f"/users/{delete_user_id}")
                if result:
                    st.success("User deleted successfully!")
                    st.rerun()
                else:
                    st.error(f"Error deleting user: {error}")
    else:
        st.info("No users found. Add some users to get started!")

elif page == "Tasks":
    st.markdown('<h1 class="main-header">📋 Tasks Management</h1>', unsafe_allow_html=True)

    # Filters
    st.subheader("Filters")
    col1, col2, col3 = st.columns(3)

    with col1:
        status_filter = st.selectbox("Filter by Status",
                                   options=["All", "pending", "in_progress", "completed"])
    with col2:
        priority_filter = st.selectbox("Filter by Priority",
                                     options=["All", "low", "medium", "high"])
    with col3:
        users = get_users()
        if users:
            owner_filter = st.selectbox("Filter by Owner",
                                      options=["All"] + [f"{user['id']} - {user['username']}" for user in users])
        else:
            owner_filter = "All"

    # Apply filters
    status = None if status_filter == "All" else status_filter
    priority = None if priority_filter == "All" else priority_filter
    owner_id = None if owner_filter == "All" else int(owner_filter.split(" - ")[0])

    tasks = get_tasks(status=status, priority=priority, owner_id=owner_id)

    if tasks:
        st.subheader(f"Tasks Found: {len(tasks)}")

        # Display tasks
        for task in tasks:
            with st.expander(f"Task #{task['id']}: {task['title']}"):
                col1, col2 = st.columns(2)

                with col1:
                    st.write(f"**Description:** {task.get('description', 'No description')}")
                    st.write(f"**Status:** {task['status']}")
                    st.write(f"**Priority:** {task['priority']}")

                with col2:
                    st.write(f"**Owner ID:** {task['owner_id']}")
                    st.write(f"**Created:** {task['created_at']}")
                    st.write(f"**Updated:** {task['updated_at']}")

                # Task actions
                action_col1, action_col2, action_col3 = st.columns(3)

                with action_col1:
                    new_status = st.selectbox(f"Update Status (Task {task['id']})",
                                            options=["pending", "in_progress", "completed"],
                                            index=["pending", "in_progress", "completed"].index(task['status']),
                                            key=f"status_{task['id']}")

                    if st.button(f"Update Status", key=f"update_status_{task['id']}"):
                        update_data = {"status": new_status}
                        result, error = make_request("PUT", f"/tasks/{task['id']}", data=update_data)
                        if result:
                            st.success("Status updated!")
                            st.rerun()
                        else:
                            st.error(f"Error: {error}")

                with action_col2:
                    new_priority = st.selectbox(f"Update Priority (Task {task['id']})",
                                              options=["low", "medium", "high"],
                                              index=["low", "medium", "high"].index(task['priority']),
                                              key=f"priority_{task['id']}")

                    if st.button(f"Update Priority", key=f"update_priority_{task['id']}"):
                        update_data = {"priority": new_priority}
                        result, error = make_request("PUT", f"/tasks/{task['id']}", data=update_data)
                        if result:
                            st.success("Priority updated!")
                            st.rerun()
                        else:
                            st.error(f"Error: {error}")

                with action_col3:
                    if st.button(f"Delete Task", key=f"delete_{task['id']}", type="primary"):
                        result, error = make_request("DELETE", f"/tasks/{task['id']}")
                        if result:
                            st.success("Task deleted!")
                            st.rerun()
                        else:
                            st.error(f"Error: {error}")
    else:
        st.info("No tasks found with the current filters.")

elif page == "Add User":
    st.markdown('<h1 class="main-header">➕ Add New User</h1>', unsafe_allow_html=True)

    with st.form("add_user_form"):
        st.subheader("User Information")

        username = st.text_input("Username", placeholder="Enter username")
        email = st.text_input("Email", placeholder="Enter email address")
        full_name = st.text_input("Full Name", placeholder="Enter full name")

        submitted = st.form_submit_button("Create User", type="primary")

        if submitted:
            if username and email and full_name:
                user_data = {
                    "username": username,
                    "email": email,
                    "full_name": full_name
                }

                result, error = make_request("POST", "/users/", data=user_data)

                if result:
                    st.success(f"User '{username}' created successfully!")
                    st.json(result)
                else:
                    st.error(f"Error creating user: {error}")
            else:
                st.error("Please fill in all fields.")

elif page == "Add Task":
    st.markdown('<h1 class="main-header">➕ Add New Task</h1>', unsafe_allow_html=True)

    users = get_users()

    if not users:
        st.error("No users found! Please create a user first.")
    else:
        with st.form("add_task_form"):
            st.subheader("Task Information")

            title = st.text_input("Task Title", placeholder="Enter task title")
            description = st.text_area("Description", placeholder="Enter task description")

            col1, col2, col3 = st.columns(3)

            with col1:
                status = st.selectbox("Status", options=["pending", "in_progress", "completed"])

            with col2:
                priority = st.selectbox("Priority", options=["low", "medium", "high"])

            with col3:
                owner_id = st.selectbox("Assign to User",
                                      options=[user['id'] for user in users],
                                      format_func=lambda x: f"{next(u['username'] for u in users if u['id'] == x)} (ID: {x})")

            due_date = st.date_input("Due Date (Optional)", value=None)

            submitted = st.form_submit_button("Create Task", type="primary")

            if submitted:
                if title and owner_id:
                    task_data = {
                        "title": title,
                        "description": description if description else None,
                        "status": status,
                        "priority": priority,
                        "owner_id": owner_id,
                        "due_date": due_date.isoformat() if due_date else None
                    }

                    result, error = make_request("POST", "/tasks/", data=task_data)

                    if result:
                        st.success(f"Task '{title}' created successfully!")
                        st.json(result)
                    else:
                        st.error(f"Error creating task: {error}")
                else:
                    st.error("Please fill in at least the title and select a user.")

# Footer
st.markdown("---")
st.markdown(
    """
    <div style="text-align: center; color: #666;">
        <p>Task Management System built with Streamlit & FastAPI</p>
        <p>API Documentation: <a href="http://localhost:8001/docs" target="_blank">http://localhost:8001/docs</a></p>
    </div>
    """,
    unsafe_allow_html=True
)