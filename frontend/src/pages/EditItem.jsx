import React, { useState, useEffect } from "react";
import { useParams, useNavigate } from "react-router-dom";
import { getItem, updateItem } from "../api/items";

export default function EditItem() {
  const { name } = useParams(); // Changed from id to name
  const navigate = useNavigate();

  const [itemData, setItemData] = useState({ name: "", description: "" });
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    async function fetchItem() {
      try {
        const res = await getItem(name);
        setItemData(res.data.item);
      } catch (err) {
        setError("Failed to fetch item");
      } finally {
        setLoading(false);
      }
    }
    fetchItem();
  }, [name]);

  const handleChange = (e) => {
    setItemData({ ...itemData, [e.target.name]: e.target.value });
  };

    const handleSubmit = async (e) => {
    e.preventDefault();
    try {
        // Send entire updated item object (name and description)
        console.log("Submitting update", {
            name: itemData.name,
            description: itemData.description,
        });

        await updateItem(itemData.name, {
        name: itemData.name,
        description: itemData.description,
        });
        navigate("/");
    } catch (err) {
        setError("Update failed");
    }
    };

  if (loading) return <p className="p-4">Loading...</p>;
  if (error) return <p className="p-4 text-red-600">{error}</p>;

  return (
    <div className="max-w-md mx-auto p-6 bg-white rounded shadow mt-8">
      <h2 className="text-2xl font-bold mb-6 text-gray-900">Edit Item</h2>
      <form onSubmit={handleSubmit} className="space-y-5">
        <div>
          <label htmlFor="name" className="block mb-2 font-semibold text-gray-700">
            Name
          </label>
          <input
            type="text"
            name="name"
            id="name"
            value={itemData.name}
            onChange={handleChange}
            className="w-full border border-gray-300 rounded px-3 py-2 focus:outline-none focus:ring-2 focus:ring-indigo-500"
            disabled // Name should not be changed on edit
          />
        </div>
        <div>
          <label htmlFor="description" className="block mb-2 font-semibold text-gray-700">
            Description
          </label>
          <textarea
            name="description"
            id="description"
            value={itemData.description}
            onChange={handleChange}
            rows={5}
            className="w-full border border-gray-300 rounded px-3 py-2 focus:outline-none focus:ring-2 focus:ring-indigo-500"
          />
        </div>
        <button
          type="submit"
          className="bg-indigo-600 text-white px-5 py-2 rounded hover:bg-indigo-700 transition"
        >
          Save Changes
        </button>
      </form>
    </div>
  );
}
