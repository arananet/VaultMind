import { Routes, Route } from "react-router-dom";
import Layout from "./components/Layout";
import QueryPage from "./pages/QueryPage";
import GuidesPage from "./pages/GuidesPage";
import DiagnosticsPage from "./pages/DiagnosticsPage";

export default function App() {
  return (
    <Routes>
      <Route element={<Layout />}>
        <Route index element={<QueryPage />} />
        <Route path="guides" element={<GuidesPage />} />
        <Route path="diagnostics" element={<DiagnosticsPage />} />
      </Route>
    </Routes>
  );
}
