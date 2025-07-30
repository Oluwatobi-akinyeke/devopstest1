import { BrowserRouter, Routes, Route } from 'react-router-dom';
import Home from './pages/Home';
import EditItem from './pages/EditItem';

function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<Home />} />
        <Route path="/edit/:name" element={<EditItem />} />
      </Routes>
    </BrowserRouter>
  );
}

export default App;