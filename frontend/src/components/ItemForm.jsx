import { useState } from "react";

export default function ItemForm({ initial, onSubmit, isEdit }) {
  const [form, setForm] = useState(initial || { name: "", description: "" });

  const handleChange = (e) => {
    setForm({ ...form, [e.target.name]: e.target.value });
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    onSubmit(form);
  };

  return (
    <form
      onSubmit={handleSubmit}
      className="bg-white p-6 rounded shadow max-w-md mx-auto space-y-6"
    >
      <h2 className="text-xl font-semibold text-gray-900">
        {isEdit ? "Edit Item" : "New Item"}
      </h2>

      <input
        type="text"
        name="name"
        placeholder="Name"
        value={form.name}
        onChange={handleChange}
        className="w-full border border-gray-300 rounded px-3 py-2 focus:outline-none focus:ring-2 focus:ring-indigo-500"
        disabled={isEdit}
        required
      />
      <textarea
        name="description"
        placeholder="Description"
        value={form.description}
        onChange={handleChange}
        className="w-full border border-gray-300 rounded px-3 py-2 focus:outline-none focus:ring-2 focus:ring-indigo-500"
        rows={4}
      />
      <button
        className="bg-green-600 text-white px-5 py-2 rounded hover:bg-green-700 transition"
        type="submit"
      >
        {isEdit ? "Update" : "Create"}
      </button>
    </form>
  );
}
