import React from "react"
import { BrowserRouter, Route, Routes } from 'react-router-dom';
import DeviceTypeOverview from "./pages/DeviceTypesOverview/DeviceTypesOverview.tsx";
import { ChatProvider } from "./context/chatContext.tsx";

import "./App.scss";
import Chat from "./components/chat/Chat.tsx";


const App: React.FC = () => {
    return (
		<BrowserRouter>
			<ChatProvider>
				<Chat />
				<Routes>

					<Route path="/" element={<DeviceTypeOverview />} />

				</Routes>
			</ChatProvider>
		</BrowserRouter>
    )
}

export default App;
