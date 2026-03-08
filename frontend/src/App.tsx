import { BrowserRouter, Navigate, Route, Routes } from "react-router-dom";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { ThemeProvider } from "./components/ThemeProvider";
import { Layout } from "./components/Layout";
import { SensorsPage } from "./pages/SensorsPage";
import { SensorDataPage } from "./pages/SensorDataPage";

const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      staleTime: 2000,
      retry: 1,
    },
  },
});

export default function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <ThemeProvider>
        <BrowserRouter>
          <Routes>
            <Route element={<Layout />}>
              <Route path="/sensors" element={<SensorsPage />} />
              <Route path="/sensor-data" element={<SensorDataPage />} />
              <Route path="*" element={<Navigate to="/sensors" replace />} />
            </Route>
          </Routes>
        </BrowserRouter>
      </ThemeProvider>
    </QueryClientProvider>
  );
}
