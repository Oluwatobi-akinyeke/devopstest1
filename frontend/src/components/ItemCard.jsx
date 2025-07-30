import { useNavigate } from "react-router-dom";

export default function ItemCard({ item, onDelete }) {
  const navigate = useNavigate();

  return (
    <div className="bg-white shadow-md rounded p-4 flex justify-between items-center">
      <div>
        <h3 className="font-bold text-lg">{item.name}</h3>
        <p className="text-gray-600">{item.description}</p>
      </div>
      <div className="space-x-2">
        <button
          onClick={() => navigate(`/edit/${item.name}`)} // 👈 Navigate to edit route
          className="px-4 py-1 bg-blue-500 text-white rounded"
        >
          Edit
        </button>
        <button
          onClick={() => onDelete(item.name)}
          className="px-4 py-1 bg-red-500 text-white rounded"
        >
          Delete
        </button>
      </div>
    </div>
  );
}
