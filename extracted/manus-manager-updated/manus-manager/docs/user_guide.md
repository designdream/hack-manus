# Manus Manager User Guide

## Introduction

Manus Manager is a comprehensive system designed to orchestrate, start, stop, and track Manus AI agents from your local machine. This guide will help you understand how to use the Manus Manager system effectively.

## Getting Started

### Accessing the System

1. Open your web browser and navigate to the Manus Manager URL provided by your administrator.
2. Log in with your username and password.
3. You will be directed to the Dashboard, which provides an overview of your agents and tasks.

### Dashboard Overview

The Dashboard displays:
- Total number of agents and tasks
- Agent status distribution (running, idle, paused, error)
- Task status distribution (completed, in progress, pending, failed)
- Overall task progress

## Managing Agents

### Viewing Agents

1. Click on "Agents" in the left sidebar to view all your agents.
2. The agent list displays each agent's name, status, maximum task capacity, and last active time.

### Creating a New Agent

1. On the Agents page, click the "Add Agent" button.
2. Fill in the required information:
   - Name: A descriptive name for your agent
   - Description: (Optional) Details about the agent's purpose
   - API Key: (Optional) If you have a specific API key for this agent
   - Max Tasks: Maximum number of tasks this agent can handle simultaneously (1-5)
3. Click "Create" to add the new agent.

### Managing Agent Status

For each agent, you can:
- **Start**: Begin agent operation (changes status to "running")
- **Pause**: Temporarily suspend agent operation (changes status to "paused")
- **Stop**: Completely stop agent operation (changes status to "idle")

To change an agent's status:
1. Find the agent in the list
2. Click the appropriate action button (Start, Pause, or Stop)

### Viewing Agent Details

1. Click on any agent in the list to view detailed information.
2. The Agent Details page shows:
   - Agent information (name, description, status)
   - Performance metrics (task completion times, success rates)
   - Task history
   - Activity logs

## Managing Tasks

### Viewing Tasks

1. Click on "Tasks" in the left sidebar to view all your tasks.
2. The task list displays each task's title, status, progress, priority, and assigned agent.

### Creating a New Task

1. On the Tasks page, click the "Add Task" button.
2. Fill in the required information:
   - Title: A descriptive title for your task
   - Description: (Optional) Details about what the task involves
   - Priority: The importance level (Low, Medium, High, Critical)
3. Click "Create" to add the new task.

### Assigning Tasks to Agents

1. Find the task you want to assign in the task list.
2. Click the "Assign" button (clipboard icon).
3. Select an agent from the dropdown menu.
4. Click "Assign" to assign the task to the selected agent.

### Updating Task Progress

1. Click on any task in the list to view detailed information.
2. On the Task Details page, click "Update Progress".
3. Enter the new progress percentage and update the status if needed.
4. Click "Update" to save the changes.

### Viewing Task Details

1. Click on any task in the list to view detailed information.
2. The Task Details page shows:
   - Task information (title, description, status)
   - Progress tracking
   - Assigned agent details
   - Activity logs
   - Timeline of status changes

## User Settings

### Updating Your Profile

1. Click on your username in the top-right corner and select "Profile" or click "Settings" in the sidebar.
2. Update your username and email as needed.
3. Click "Update Profile" to save changes.

### Changing Your Password

1. Navigate to the Settings page.
2. Enter your current password and new password.
3. Confirm your new password.
4. Click "Change Password" to update.

## Troubleshooting

### Common Issues

1. **Agent not starting**: 
   - Check if the agent has reached its maximum task limit
   - Verify the agent's API key is valid
   - Check the agent logs for specific error messages

2. **Task stuck in pending status**:
   - Ensure the task is assigned to an agent
   - Verify the assigned agent is in "running" status
   - Check if the agent has capacity to handle more tasks

3. **Connection issues**:
   - Verify your internet connection
   - Check if the Manus Manager server is online
   - Try refreshing the page or logging out and back in

### Getting Help

If you encounter issues not covered in this guide, please contact your system administrator or support team.

## Best Practices

1. **Agent Management**:
   - Name agents descriptively based on their purpose
   - Regularly check agent performance metrics
   - Stop idle agents to conserve resources

2. **Task Organization**:
   - Use clear, descriptive task titles
   - Set appropriate priority levels
   - Break complex tasks into smaller, manageable tasks

3. **Monitoring**:
   - Regularly check the Dashboard for system overview
   - Review agent and task logs for potential issues
   - Update task progress regularly for accurate reporting
