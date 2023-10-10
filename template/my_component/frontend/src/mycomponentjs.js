import React from "react";
import {
    Streamlit,
    StreamlitComponentBase,
    withStreamlitConnection,
} from "streamlit-component-lib";
import DataTable from "react-data-table-component";

const customStyles = {
    head: {
        style: {
            fontSize: "14px",
            color: "#333",
        },
    },
};


class MyComponent extends StreamlitComponentBase {
    constructor(props) {
        super(props);
        this.state = {
            numClicks: 0,
            isFocused: false,
            df1: JSON.parse(props.args["df1"]), // Parse df1 and set it in the state
            df2: {},
        };

        this.handleCheckboxChange = this.handleCheckboxChange.bind(this);
    }

    componentDidUpdate(prevProps) {
        // If props has changed
        if (this.props.args["df1"] !== prevProps.args["df1"]) {
            // Parse the new df1 and update the state
            this.setState({ df1: JSON.parse(this.props.args["df1"]) });
        }
    }

    handleCheckboxChange = (row) => {
        const newData = [...this.state.df1];
        const index = newData.findIndex((r) => r.id === row.id); // replace 'id' with your unique identifier

        newData[index] = {
            ...newData[index],
            likely_fixed: !newData[index].likely_fixed,
        };
        this.setState({ df1: newData });
    };
    handleRowSelected = (state) => {
        console.log('Selected Rows: ', state.selectedRows);
    };

    render = () => {
        const name = this.props.args["name"];
        const columns = [
            {
                name: 'Likely_fixed',
                selector: row => row.likely_fixed,
                cell: (row) => (
                    <input
                        type="checkbox"
                        checked={row.likely_fixed}
                        // onChange={() => this.handleCheckboxChange(row)}
                        disabled
                        style={{ width: '20px', height: '20px' }}
                    />
                ),
                center: true,
                compact: true,
            },
            { name: 'imo', selector: row => row.imo, center: true, compact: true },
            { name: 'name', selector: row => row.Name, center: true, compact: true},
            { name: 'dwt', selector: row => row.dwt, center: true, maxWidth: 15},
            { name: 'draught', selector: row => row.draught, center: true},
            {
                name: 'scrubber',
                selector: row => row.scrubber,
                cell: (row) => (
                    <input
                        type="checkbox"
                        checked={row.scrubber}
                        disabled
                        style={{ width: '20px', height: '20px' }}
                        readOnly
                    />
                ),
                center: true
                , compact: true 
            },
            { name: 'age', selector: row => row.age, center: true, compact: true },
            {
                name: 'isopen_med',
                selector: row => row.isopen_med,
                cell: (row) => (
                    <input
                        type="checkbox"
                        checked={row.isopen_med}
                        disabled
                        style={{ width: '20px', height: '20px' }}
                        readOnly
                    />
                ),
                center: true
            },
            {
                name: 'isopen_nwe',
                selector: row => row.isopen_nwe,
                cell: (row) => (
                    <input
                        type="checkbox"
                        checked={row.isopen_nwe}
                        disabled
                        style={{ width: '20px', height: '20px' }}
                        readOnly
                    />
                ),
                center: true
            },
            { name: 'open', selector: row => row.Open, center: true, allowOverflow: true},
            { name: 'open date', selector: row => row.OpenDate, center: true},
            { name: 'ETA Gibraltar', selector: row => row.ETAGibraltar, center: true, compact: true},
            { name: 'speed', selector: row => row.Speed, center: true},
            { name: 'operator', selector: row => row.current_operator, center: true, compact: true, },
            { name: 'ais_destination', selector: row => row.ais_destination_now, center: true, compact: true},
        
            // ...rest of your columns
        ];
        return (
            <span>
                <span className="card text-center mb-3">
                    <div>
                        <DataTable
                            columns={columns}
                            data={this.state.df1} 
                            highlightOnHover
                            responsive='true'
                            striped='true'
                            selectableRows
                            onSelectedRowsChange={this.handleRowSelected}
                            customStyles={customStyles}
                        />
                    </div>
                    <br />
                    <br />
                </span>
            </span>
        );
    };
}

export default withStreamlitConnection(MyComponent);
