import { useCallback, useEffect, useState } from "react";
import { api } from "./api";

const STATUSES = [
  { value: "todo", label: "To do" },
  { value: "in_progress", label: "In progress" },
  { value: "done", label: "Done" },
];
const EMPTY_FORM = { title: "", description: "", priority: "medium", due_date: "" };

function TaskForm({ onCreate }) {
  const [form, setForm] = useState(EMPTY_FORM);
  const update = (field) => (e) => setForm({ ...form, [field]: e.target.value });

  const submit = async (e) => {
    e.preventDefault();
    await onCreate({ ...form, due_date: form.due_date || null });
    setForm(EMPTY_FORM);
  };

  return (
    <form className="card form" onSubmit={submit}>
      <input placeholder="Task title" value={form.title} onChange={update("title")} required />
      <input placeholder="Description (optional)" value={form.description} onChange={update("description")} />
      <select value={form.priority} onChange={update("priority")}>
        <option value="low">Low priority</option>
        <option value="medium">Medium priority</option>
        <option value="high">High priority</option>
      </select>
      <input type="date" value={form.due_date} onChange={update("due_date")} />
      <button type="submit">Add task</button>
    </form>
  );
}

function TaskItem({ task, onUpdate, onDelete }) {
  const overdue = task.due_date && task.status !== "done" && new Date(task.due_date) < new Date().setHours(0, 0, 0, 0);
  return (
    <li className={`card task ${task.status}`}>
      <div>
        <strong>{task.title}</strong>
        <span className={`badge ${task.priority}`}>{task.priority}</span>
        {task.description && <p>{task.description}</p>}
        {task.due_date && <small className={overdue ? "overdue" : ""}>Due {task.due_date}</small>}
      </div>
      <div className="actions">
        <select value={task.status} onChange={(e) => onUpdate(task.id, { status: e.target.value })}>
          {STATUSES.map((s) => <option key={s.value} value={s.value}>{s.label}</option>)}
        </select>
        <button className="danger" onClick={() => onDelete(task.id)}>Delete</button>
      </div>
    </li>
  );
}

export default function App() {
  const [tasks, setTasks] = useState([]);
  const [stats, setStats] = useState(null);
  const [filter, setFilter] = useState("");
  const [search, setSearch] = useState("");
  const [error, setError] = useState("");

  const load = useCallback(async () => {
    try {
      const [list, s] = await Promise.all([api.listTasks({ status: filter, search }), api.stats()]);
      setTasks(list);
      setStats(s);
      setError("");
    } catch (err) {
      setError(err.message);
    }
  }, [filter, search]);

  useEffect(() => { load(); }, [load]);

  // Run an API call, then refresh the list; show any error at the top.
  const run = (fn) => async (...args) => {
    try {
      await fn(...args);
      await load();
    } catch (err) {
      setError(err.message);
    }
  };

  return (
    <main>
      <h1>Task Manager</h1>
      {stats && (
        <div className="stats">
          <span>Total: {stats.total}</span>
          {STATUSES.map((s) => <span key={s.value}>{s.label}: {stats.by_status[s.value]}</span>)}
          <span className="overdue">Overdue: {stats.overdue}</span>
        </div>
      )}
      {error && <div className="error">{error}</div>}

      <TaskForm onCreate={run(api.createTask)} />

      <div className="filters">
        <input placeholder="Search tasks..." value={search} onChange={(e) => setSearch(e.target.value)} />
        <select value={filter} onChange={(e) => setFilter(e.target.value)}>
          <option value="">All statuses</option>
          {STATUSES.map((s) => <option key={s.value} value={s.value}>{s.label}</option>)}
        </select>
      </div>

      <ul className="list">
        {tasks.map((t) => (
          <TaskItem key={t.id} task={t} onUpdate={run(api.updateTask)} onDelete={run(api.deleteTask)} />
        ))}
        {tasks.length === 0 && <li className="empty">No tasks yet.</li>}
      </ul>
    </main>
  );
}
