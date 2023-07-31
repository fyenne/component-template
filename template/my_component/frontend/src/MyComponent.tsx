import {
  Streamlit,
  StreamlitComponentBase,
  withStreamlitConnection,
} from "streamlit-component-lib"
import DataTable from "react-data-table-component"
import React, { ReactNode, useState } from "react"

interface State {
  numClicks: number
  isFocused: boolean
  ls: string[]
  df1: any
  df2: any
}

interface CustomCellProps {
  value: string
  tooltipContent: string
}

interface DataRow {
  open_period: string
  diff: number
  order_key: string
  new: boolean
  likely_fixed: boolean
}
 

const CustomCell = ({ value }: { value: any }) => {
  const [hovered, setHovered] = useState(false)
  return (
    <div
      onMouseEnter={() => setHovered(true)}
      onMouseLeave={() => setHovered(false)}
    >
      {hovered ? <div>
        hahshd
      </div> : value}
    </div>
  )
}

class MyComponent extends StreamlitComponentBase<State> {
  public state = {
    numClicks: 0,
    isFocused: false,
    ls: [],
    df1: {},
    df2: {},
  }
  

  public render = (): ReactNode => { 
    const name = this.props.args["name"] 
    const df1 = JSON.parse(this.props.args["df1"]) as any[]
    const df2 = JSON.parse(this.props.args["df2"]) as any[] 
    const { theme } = this.props
    const style: React.CSSProperties = {} 
    if (theme) { 
      const borderStyling = `1px solid ${
        this.state.isFocused ? theme.primaryColor : "gray"
      }`
      style.border = borderStyling
      style.outline = borderStyling
    } 
    return (
      <span className="card text-center border-success mb-3">
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
                cell:  (row: DataRow) => <CustomCell value={row.diff} />,
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
                selector: (row) => row.roll1,
              },
            ]}
            data={df1}
          ></DataTable>
        </div>
        <br />
        <br />
        <button
          style={style}
          onClick={this.onClicked}
          disabled={this.props.disabled}
          onFocus={this._onFocus}
          onBlur={this._onBlur}
        >
          Click Me!
        </button>
      </span>
    )
  }
 
  private onClicked = (): void => { 
    this.setState(
      (prevState) => ({ numClicks: prevState.numClicks + 1 }),
      () => Streamlit.setComponentValue(this.state.numClicks)
    )
  } 
  private _onFocus = (): void => {
    this.setState({ isFocused: true })
  }
 
  private _onBlur = (): void => {
    this.setState({ isFocused: false })
  }
} 
export default withStreamlitConnection(MyComponent)
