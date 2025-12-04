import { useEffect, useState } from 'react';
import { getItems, deleteItem, createItem } from '../api/items';
import ItemCard from '../components/ItemCard';
import ItemForm from '../components/ItemForm';

export default function Home() {
  const [items, setItems] = useState([]);
  const [showForm, setShowForm] = useState(false);

  const fetchItems = async () => {
    try {
      const res = await getItems();
      setItems(res.data.items);
    } catch (err) {
      console.error('Failed to fetch items', err);
    }
  };

  useEffect(() => {
    fetchItems();
  }, []);

  const handleCreate = async (data) => {
    try {
      await createItem(data);
      setShowForm(false);
      fetchItems();
    } catch (err) {
      console.error('Create failed', err);
    }
  };

  const handleDelete = async (name) => {
    try {
      await deleteItem(name);
      fetchItems();
    } catch (err) {
      console.error('Delete failed', err);
    }
  };

  return (
    <div className="p-8 space-y-6 bg-gray-50 min-h-screen">
      <div className="flex justify-between items-center">
        <h1 className="text-3xl font-bold text-gray-900 mb-8">Inventory Manager</h1>
        <button
          onClick={() => setShowForm(!showForm)}
          className="bg-indigo-600 text-white px-5 py-2 rounded hover:bg-indigo-700 transition"
        >
          {showForm ? 'Cancel' : 'Add Item'}
        </button>
      </div>

      {showForm && (
        <ItemForm
          onSubmit={handleCreate}
        />
      )}

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {items?.map(item => (
          <ItemCard
            key={item.name}
            item={item}
            onDelete={handleDelete}
          />
        ))}
      </div>
    </div>
  );
}
