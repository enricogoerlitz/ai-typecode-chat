import React from "react"
import { BrowserRouter, Route, Routes } from 'react-router-dom';
import DeviceTypeOverview from "./pages/DeviceTypesOverview.tsx";
import { ChatProvider } from "./context/chatContext.tsx";


const App: React.FC = () => {
    return (
		<BrowserRouter>
			<ChatProvider>
				<Routes>

					<Route path="/" element={<DeviceTypeOverview />} />

				</Routes>
			</ChatProvider>
		</BrowserRouter>
    )
}

export default App;
