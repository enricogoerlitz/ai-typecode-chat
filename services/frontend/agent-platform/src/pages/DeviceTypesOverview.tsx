import React, { useContext, useState } from "react"
import { ChatContext, IChatContext } from "../context/chatContext.tsx";
import ReactMarkdown from "react-markdown"
import deviceTypeData from "../assets/deviceTypesData.json";

const typeCodes: Array<any> = deviceTypeData;

const DeviceTypeOverview: React.FC = () => {
    const { setTypeCodeID, typeCode } = useContext(ChatContext) as IChatContext;
    const [searchTerm, setSearchTerm] = useState("")

    const markDownData = "```json\n" + JSON.stringify(typeCode, null, 4) + "\n```"
    return (
        <div>
            <h1>DeviceTypes (Selected: {typeCode?.Typcode || "nothing"})</h1>
            <input onChange={(e) => setSearchTerm(e.target.value)} value={searchTerm} />
            <table>
                <thead>
                    <tr>
                        <td>Typcode</td>
                        <td>Getät ID</td>
                        <td>Typ Modell</td>
                        <td>Geraetebezeichnung</td>
                    </tr>
                </thead>
                <tbody>
                    {typeCodes.filter(typeCode => typeCode.Typcode.includes(searchTerm)).map((typeCode) => (
                        <tr
                            key={typeCode.Typcode}
                            onClick={() => setTypeCodeID(typeCode.Typcode)}
                        >
                            <td>{typeCode.Typcode}</td>
                            <td>{typeCode.GeraetID}</td>
                            <td>{typeCode.Typ_Modell}</td>
                            <td>{typeCode.Geraetebezeichnung}</td>
                        </tr>
                    ))}
                </tbody>
            </table>
            <ReactMarkdown>{markDownData}</ReactMarkdown>
        </div>
    )
}

export default DeviceTypeOverview;
