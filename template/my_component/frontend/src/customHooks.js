
const columns = [
    {
        name: 'Likely_fixed',
        selector: row => row.likely_fixed,
        cell: (row) => (
            <input
                type="checkbox"
                checked={row.likely_fixed}
                enabled
                onChange={() => handleCheckboxChange(row)}
                style={{ width: '20px', height: '20px' }}
            />
        ),
        center: true
        , compact: true 
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

];
