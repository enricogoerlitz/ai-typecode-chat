import React, { useContext, useState } from "react"
import { ChatContext, IChatContext } from "../../context/chatContext.tsx";
import deviceTypeData from "../../assets/deviceTypesData.json";
import "./DeviceTypesOverview.scss"

const typeCodes: Array<any> = deviceTypeData;

const DeviceTypeOverview: React.FC = () => {
    const { setTypeCodeID, typeCode } = useContext(ChatContext) as IChatContext;
    const [searchTerm, setSearchTerm] = useState("")

    /*
        const markDownData = "```json\n" + JSON.stringify(typeCode, null, 4) + "\n```"
        {typeCode && (
            <div className="dto-content-container__typecode-json">
                <ReactMarkdown>{markDownData}</ReactMarkdown>
            </div>
        )}
    */

        
    const filteredTypeCodes = typeCodes.filter(tcode => (
        tcode.Typcode.includes(searchTerm) ||
        tcode.GeraetID.includes(searchTerm) ||
        tcode.Typ_Modell.includes(searchTerm) ||
        tcode.Geraetebezeichnung.includes(searchTerm)
    ));

    return (
        <div className="dto-container">
            <div className="dto-container__header">
                <h1>Übersicht: IMT Typcodes</h1>
            </div>
            <div className="dto-content-container">
                <div className="dto-content-container__typecode-list">
                    <h3 className="dto-content-container__typecode-list__header">Typcode Liste</h3>
                    <input
                        className="search-typecodes"
                        onChange={(e) => setSearchTerm(e.target.value)}
                        value={searchTerm}
                        placeholder="Suche nach Typcode &nbsp;🎓"
                    />
                    <table className="typecode-table">
                        <thead>
                            <tr>
                                <th>Typcode</th>
                                <th>Getät ID</th>
                                <th>Typ Modell</th>
                                <th>Geraetebezeichnung</th>
                            </tr>
                        </thead>
                        <tbody>
                            {filteredTypeCodes.map((tCode) => (
                                <tr
                                    key={tCode.Typcode}
                                    onClick={() => setTypeCodeID(tCode.Typcode)}
                                    className={tCode.Typcode === typeCode?.Typcode ? "selected" : ""}
                                >
                                    <td>{tCode.Typcode}</td>
                                    <td>{tCode.GeraetID}</td>
                                    <td>{tCode.Typ_Modell}</td>
                                    <td>{tCode.Geraetebezeichnung}</td>
                                </tr>
                            ))}
                        </tbody>
                    </table>
                </div>
            </div>
        </div>
    )
}

export default DeviceTypeOverview;
