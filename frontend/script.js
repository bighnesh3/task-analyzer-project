// script.js

// State management
let taskCounter = 0;

// Strategy descriptions
const strategyDescriptions = {
    smart: '<strong>Smart Balance:</strong> Balances urgency, importance, effort, and dependencies equally',
    fast: '<strong>Fastest Wins:</strong> Prioritizes low-effort tasks for quick completion',
    impact: '<strong>High Impact:</strong> Focuses on importance over everything else',
    deadline: '<strong>Deadline Driven:</strong> Heavily weights tasks by due date urgency'
};

// DOM Elements
const taskList = document.getElementById('taskList');
const addTaskBtn = document.getElementById('addTaskBtn');
const analyzeBtn = document.getElementById('analyzeBtn');
const suggestBtn = document.getElementById('suggestBtn');
const clearBtn = document.getElementById('clearBtn');
const loadBulkBtn = document.getElementById('loadBulkBtn');
const bulkTaskInput = document.getElementById('bulkTaskInput');
const strategyDropdown = document.getElementById('strategy');
const strategyDescription = document.getElementById('strategy-description');
const loadingIndicator = document.getElementById('loadingIndicator');
const outputSection = document.getElementById('outputSection');
const resultsGrid = document.getElementById('resultsGrid');
const warningsContainer = document.getElementById('warningsContainer');
const warningsList = document.getElementById('warningsList');

// Initialize with 2 empty tasks
function init() {
    addTask();
    addTask();
}

// Add a new task row
function addTask(taskData = {}) {
    taskCounter++;
    const taskId = taskData.id || `task_${taskCounter}`;
    
    const taskRow = document.createElement('div');
    taskRow.className = 'task-row';
    taskRow.dataset.taskId = taskId;
    
    taskRow.innerHTML = `
        <div class="input-group">
            <label>ID</label>
            <input type="text" class="task-id" value="${taskData.id || ''}" placeholder="Enter task ID">
        </div>
        <div class="input-group">
            <label>Title</label>
            <input type="text" class="task-title" value="${taskData.title || ''}" placeholder="Enter task title" required>
        </div>
        <div class="input-group">
            <label>Due Date</label>
            <input type="date" class="task-due-date" value="${taskData.due_date || ''}" required>
        </div>
        <div class="input-group">
            <label>Effort (hours)</label>
            <input type="number" class="task-hours" value="${taskData.estimated_hours || ''}" placeholder="Enter effort(hours)" min="0.1" step="0.5" max="8" required>  <!-- max 8 assuming an 8-hour at office -->
        </div>
        <div class="input-group">
            <label>Importance (1-10)</label>
            <input type="number" class="task-importance" value="${taskData.importance || ''}" placeholder="Enter importance" min="1" max="10" required>
        </div>
        <div class="input-group">
            <label>Dependencies</label>
            <input type="text" class="task-dependencies" value="${taskData.dependencies ? taskData.dependencies.join(', ') : ''}" placeholder="eg. task_1, task_2">
            <small>Comma-separated IDs</small>
        </div>
        <div class="input-group">
            <button class="btn btn-danger remove-task-btn" onclick="removeTask('${taskId}')">Remove</button>
        </div>
    `;
    
    taskList.appendChild(taskRow);
}

// Remove a task row
function removeTask(taskId) {
    const taskRow = document.querySelector(`[data-task-id="${taskId}"]`);
    if (taskRow) {
        taskRow.remove();
    }
}

// Gather all tasks from form
// Gather all tasks from form
// Returns an array of task objects or null if validation failed (frontend prompts user)
function gatherTasks() {
    const tasks = [];
    const taskRows = document.querySelectorAll('.task-row');

    for (let i = 0; i < taskRows.length; i++) {
        const row = taskRows[i];
        const id = row.querySelector('.task-id').value.trim();
        const title = row.querySelector('.task-title').value.trim();
        const due_date = row.querySelector('.task-due-date').value;
        const estimated_hours_raw = row.querySelector('.task-hours').value.trim();
        const importance_raw = row.querySelector('.task-importance').value.trim();
        const dependenciesStr = row.querySelector('.task-dependencies').value.trim();

        // Required fields: id, title, due_date
        if (!id) {
            alert(`Please provide an ID for task #${i + 1}.`);
            return null;
        }
        if (!title) {
            alert(`Please provide a Title for task "${id}".`);
            return null;
        }
        if (!due_date) {
            alert(`Please provide a Due Date for task "${id}".`);
            return null;
        }

        // Parse dependencies into array
        const dependencies = dependenciesStr
            ? dependenciesStr.split(',').map(d => d.trim()).filter(d => d)
            : [];

        // Validate numeric fields
        // estimated_hours: if empty -> use default 1 (and mark usedDefault)
        // if present but invalid (non-numeric or <=0) -> prompt user (block)
        let estimated_hours;
        let usedDefaultHours = false;
        if (estimated_hours_raw === '') {
            estimated_hours = null; // default
            usedDefaultHours = true;
        } else {
            estimated_hours = parseFloat(estimated_hours_raw);
            if (isNaN(estimated_hours) || estimated_hours <= 0) {
                alert(`Invalid Effort for task "${id}". Please enter a positive number (e.g., 1, 2.5).`);
                return null;
            }
        }

        // importance: if empty -> default 5
        // if present but invalid (non-numeric or out of range 1-10) -> prompt user (block)
        let importance;
        let usedDefaultImportance = false;
        if (importance_raw === '') {
            importance = null; // default
            usedDefaultImportance = true;
        } else {
            importance = parseFloat(importance_raw);
            if (isNaN(importance) || importance < 1 || importance > 10) {
                alert(`Invalid Importance for task "${id}". Please enter a number between 1 and 10.`);
                return null;
            }
        }

        // Build the task object. Also add a small client-side marker for defaults used.
        const task = {
            id,
            title,
            due_date,
            estimated_hours,
            importance,
            dependencies,
            _client_used_defaults: {
                estimated_hours: usedDefaultHours,
                importance: usedDefaultImportance
            }
        };

        tasks.push(task);
    }

    return tasks;
}


// Load tasks from bulk JSON input
function loadBulkTasks() {
    const jsonStr = bulkTaskInput.value.trim();
    
    if (!jsonStr) {
        alert('Please paste JSON tasks first');
        return;
    }
    
    try {
        const tasks = JSON.parse(jsonStr);
        
        if (!Array.isArray(tasks)) {
            throw new Error('JSON must be an array of tasks');
        }
        
        // Clear existing tasks
        taskList.innerHTML = '';
        taskCounter = 0;
        
        // Add each task
        tasks.forEach(task => addTask(task));
        
        bulkTaskInput.value = '';
        alert(`Loaded ${tasks.length} tasks successfully!`);
        
    } catch (error) {
        alert(`Invalid JSON: ${error.message}`);
    }
}

// Clear all tasks and results
function clearAll() {
    if (confirm('Clear all tasks and results?')) {
        taskList.innerHTML = '';
        taskCounter = 0;
        outputSection.style.display = 'none';
        resultsGrid.innerHTML = '';
        bulkTaskInput.value = '';
        addTask();
        addTask();
    }
}

// Call analyze API
async function analyzeTasks() {
    const tasks = gatherTasks();
    if (tasks === null) return; // validation failed and user alerted

    if (tasks.length === 0) {
        alert('Please add at least one task');
        return;
    }

    const strategy = strategyDropdown.value;
    // show loading...
    loadingIndicator.style.display = 'block';
    outputSection.style.display = 'none';
    
    try {
        const response = await fetch('/api/tasks/analyze/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                tasks,
                strategy
            })
        });
        
        if (!response.ok) {
            const errorData = await response.json();
            throw new Error(errorData.error || 'Analysis failed');
        }
        
        const result = await response.json();
        displayResults(result, 'All Tasks Analysis');
        const anyUsedDefaults = result.tasks.some(t => (t._client_used_defaults && (t._client_used_defaults.estimated_hours || t._client_used_defaults.importance)) || (t.validation_warnings && t.validation_warnings.length > 0));
        if (anyUsedDefaults) {
            // show a non-blocking notice
            setTimeout(() => {
                alert('Note: some tasks used default effort/importance values. Check the result cards for warnings.');
            }, 200);
        }
        
    } catch (error) {
        alert(`Error: ${error.message}`);
    } finally {
        loadingIndicator.style.display = 'none';
    }
}

// Call suggest API
async function suggestTasks() {
    const tasks = gatherTasks();
    if (tasks === null) return;

    if (tasks.length === 0) {
        alert('Please add at least one task');
        return;
    }
    
    const strategy = strategyDropdown.value;
    
    // Show loading
    loadingIndicator.style.display = 'block';
    outputSection.style.display = 'none';
    
    try {
        const response = await fetch('/api/tasks/suggest/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                tasks,
                strategy
            })
        });
        
        if (!response.ok) {
            const errorData = await response.json();
            throw new Error(errorData.error || 'Suggestion failed');
        }
        
        const result = await response.json();
        displayResults({
            tasks: result.suggestions,
            warnings: result.warnings
        }, 'Top 3 Suggested Tasks');
        const anyUsedDefaults = result.tasks.some(t => (t._client_used_defaults && (t._client_used_defaults.estimated_hours || t._client_used_defaults.importance)) || (t.validation_warnings && t.validation_warnings.length > 0));
        if (anyUsedDefaults) {
            // show a non-blocking notice
            setTimeout(() => {
                alert('Note: some tasks used default effort/importance values. Check the result cards for warnings.');
            }, 200);
        }
        
    } catch (error) {
        alert(`Error: ${error.message}`);
    } finally {
        loadingIndicator.style.display = 'none';
    }
}

// Display results
function displayResults(result, title) {
    // Show output section
    outputSection.style.display = 'block';
    
    // Display warnings
    if (result.warnings && result.warnings.length > 0) {
        warningsContainer.style.display = 'block';
        warningsList.innerHTML = '';
        result.warnings.forEach(warning => {
            const li = document.createElement('li');
            li.textContent = warning;
            warningsList.appendChild(li);
        });
    } else {
        warningsContainer.style.display = 'none';
    }
    
    // Display results
    resultsGrid.innerHTML = '';
    
    if (result.tasks.length === 0) {
        resultsGrid.innerHTML = '<p style="text-align: center; color: #666;">No tasks to display</p>';
    } else {
        result.tasks.forEach((task, index) => {
            const card = createResultCard(task, index + 1);
            resultsGrid.appendChild(card);
        });
    }
    
    // Scroll to results
    outputSection.scrollIntoView({ behavior: 'smooth', block: 'start' });
}

// Create a result card
function createResultCard(task, rank) {
    const card = document.createElement('div');
    const priorityClass = task.priority ? task.priority.toLowerCase() : 'low';
    card.className = `result-card priority-${priorityClass}`;
    
    const badges = [];
    if (task.past_due) {
        badges.push('<span class="past-due-badge">PAST DUE</span>');
    }
    if (task.dependency_issue) {
        badges.push('<span class="dependency-issue-badge">⚠ CIRCULAR DEPENDENCY</span>');
    }

    // client-side defaults marker (if backend echoes this field back, use that; else rely on client marker)
    const usedDefaults = task._client_used_defaults || {};
    // backend may also include validation_warnings and confidence
    const validationWarnings = task.validation_warnings || [];

    if (usedDefaults.estimated_hours) {
        badges.push('<span class="dependency-issue-badge">⚠ Used default effort (1h)</span>');
    }
    if (usedDefaults.importance) {
        badges.push('<span class="dependency-issue-badge">⚠ Used default importance (5)</span>');
    }

    // If backend flagged missing fields in validation_warnings, show a badge too
    if (validationWarnings.length > 0) {
        badges.push('<span class="dependency-issue-badge">⚠ Missing data</span>');
    }

    const scoreDisplay = (typeof task.score !== 'undefined') ? task.score : '—';
    const dueDateDisplay = task.due_date || '—';
    const effortDisplay = (typeof task.estimated_hours !== 'undefined' && task.estimated_hours !== null) ? `${task.estimated_hours} hours` : '—';
    const importanceDisplay = (typeof task.importance !== 'undefined' && task.importance !== null) ? `${task.importance}/10` : '—';

    // Build warnings HTML (backend validation_warnings)
    const warningsHtml = (validationWarnings.length > 0)
        ? `<div class="warning-list"><strong>Warnings:</strong><br>${validationWarnings.map(w => `• ${w}`).join('<br>')}</div>`
        : '';

    

    card.innerHTML = `
        <div class="result-header">
            <div class="result-title">#${rank} ${task.title}</div>
            <span class="priority-badge ${priorityClass}">${task.priority || 'N/A'}</span>
        </div>
        
        <div class="score-display">Score: ${scoreDisplay}</div>
        
        <div class="result-details">
            <div class="detail-item">
                <span class="detail-label">Task ID:</span>
                <span class="detail-value">${task.id}</span>
            </div>
            <div class="detail-item">
                <span class="detail-label">Due Date:</span>
                <span class="detail-value">${dueDateDisplay}</span>
            </div>
            <div class="detail-item">
                <span class="detail-label">Effort:</span>
                <span class="detail-value">${effortDisplay}</span>
            </div>
            <div class="detail-item">
                <span class="detail-label">Importance:</span>
                <span class="detail-value">${importanceDisplay}</span>
            </div>
            <div class="detail-item">
                <span class="detail-label">Dependencies:</span>
                <span class="detail-value">${task.dependencies && task.dependencies.length > 0 ? task.dependencies.join(', ') : 'None'}</span>
            </div>
        </div>
        
        ${badges.length > 0 ? badges.join(' ') : ''}

        <div class="explanation">
            ${warningsHtml}
            <strong>Why this score?</strong><br>
            ${task.explanation || '—'}
        </div>
    `;
    
    return card;
}


// Update strategy description
function updateStrategyDescription() {
    const strategy = strategyDropdown.value;
    strategyDescription.innerHTML = strategyDescriptions[strategy];
}

// Event Listeners
addTaskBtn.addEventListener('click', () => addTask());
analyzeBtn.addEventListener('click', analyzeTasks);
suggestBtn.addEventListener('click', suggestTasks);
clearBtn.addEventListener('click', clearAll);
loadBulkBtn.addEventListener('click', loadBulkTasks);
strategyDropdown.addEventListener('change', updateStrategyDescription);

// Initialize
init();