import React, { useState } from "react";
import {
    Streamlit,
    StreamlitComponentBase,
    withStreamlitConnection,
} from "streamlit-component-lib";
import DataTable from "react-data-table-component";

const CustomCell = ({ df_detailed , value}) => {
    const [hovered, setHovered] = useState(false);
    const df2_sub = df_detailed.filter((row) => row.open_period === value.open_period);
    return (
        <div
            onMouseDown={() => setHovered(true)}
            onMouseUp={() => setHovered(false)}
        >
            {hovered ? <div>
                <DataTable
                columns={[
                    {
                        selector: (row) => row.gone,
                    },
                ]}
                data = {df2_sub}></DataTable>
            </div> : value.gone}
        </div>
    );
}; 


class MyComponent extends StreamlitComponentBase {
    state = {
        numClicks: 0,
        isFocused: false,
        df1: {},
        df2: {},
    };

    render = () => {
        const name = this.props.args["name"];
        const df1 = JSON.parse(this.props.args["df1"]);
        const df2 = JSON.parse(this.props.args["df2"]);
        
        return (
            <span className="card text-center mb-3">
                Hello, {name}! &nbsp;
                <br />
                <br />
                <div>
                    <DataTable
                        columns={[
                            {
                                name: "open_period",
                                selector: (row) => row.open_period,
                                cell: (row) => (
                                    <div>
                                        <span title={row.new}>{row.open_period}</span>
                                    </div>
                                ),
                            },
                            {
                                name: "diff",
                                selector: (row) => row.diff,
                                cell: (row) => <CustomCell df_detailed={df1} value={row}/>,
                            },
                            {
                                name: "oerder_key",
                                selector: (row) => row.order_key,
                            },
                            {
                                name: "new",
                                selector: (row) => row.new,
                            },
                            {
                                name: "likely_fixed",
                                selector: (row) => row.likely_fixed,
                            },
                            {
                                name: "roll",
                                selector: (row) => row.roll,
                            },
                            {
                                name: "gone",
                                selector: (row) => row.gone,
                                cell: (row) => <CustomCell df_detailed={df1} value={row} />,
                            },
                        ]}
                        data={df2}
                    ></DataTable>
                <span>---</span>
                <DataTable
                columns={[
                    {
                        name: "open_period",
                        selector: (row) => row.open_period,
                        
                    },
                    {
                        name: "new",
                        selector: (row) => row.new,
                    },
                    {
                        name: "roll",
                        selector: (row) => row.roll1,
                    },
                    {
                        name: "gone",
                        selector: (row) => row.gone,
                    },
                ]}
                data={df1}>
                </DataTable>
                </div>
                <br />
                <br />
            </span>
        );
    };

}
export default withStreamlitConnection(MyComponent);