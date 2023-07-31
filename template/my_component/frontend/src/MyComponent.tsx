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
  name_: string
  additionalInfo: string
}

interface HoveredRow {
  name: string
  // other properties
}

const CustomCell: React.FC<CustomCellProps> = ({ value, tooltipContent }) => {
  const [showTooltip, setShowTooltip] = useState(false)

  return (
    <div
      onMouseEnter={() => setShowTooltip(true)}
      onMouseLeave={() => setShowTooltip(false)}
    >
      {value}
      {showTooltip && <div className="tooltip">{tooltipContent}</div>}
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
    // Arguments that are passed to the plugin in Python are accessible
    // via `this.props.args`. Here, we access the "name" arg.
    const name = this.props.args["name"]
    // const ls = JSON.parse(this.props.args["ls"]) as string[]
    const df1 = JSON.parse(this.props.args["df1"]) as any[]
    const df2 = JSON.parse(this.props.args["df2"]) as any[]

    // Streamlit sends us a theme object via props that we can use to ensure
    // that our component has visuals that match the active theme in a
    // streamlit app.
    const { theme } = this.props
    const style: React.CSSProperties = {}
    // Maintain compatibility with older versions of Streamlit that don't send
    // a theme object.
    if (theme) {
      // Use the theme object to style our button border. Alternatively, the
      // theme style is defined in CSS vars.
      const borderStyling = `1px solid ${
        this.state.isFocused ? theme.primaryColor : "gray"
      }`
      style.border = borderStyling
      style.outline = borderStyling
    }

    // Show a button and some text.
    // When the button is clicked, we'll increment our "numClicks" state
    // variable, and send its new value back to Streamlit, where it'll
    // be available to the Python program.
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
                // cell: (row: DataRow) => (
                //     <CustomCell value={row.name} tooltipContent={row.additionalInfo} />
                //   ),
              },
              {
                name: "diff",
                selector: (row) => row.diff,
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

  /** Click handler for our "Click Me!" button. */
  private onClicked = (): void => {
    // Increment state.numClicks, and pass the new value back to
    // Streamlit via `Streamlit.setComponentValue`.
    this.setState(
      (prevState) => ({ numClicks: prevState.numClicks + 1 }),
      () => Streamlit.setComponentValue(this.state.numClicks)
    )
  }

  /** Focus handler for our "Click Me!" button. */
  private _onFocus = (): void => {
    this.setState({ isFocused: true })
  }

  /** Blur handler for our "Click Me!" button. */
  private _onBlur = (): void => {
    this.setState({ isFocused: false })
  }
}

// "withStreamlitConnection" is a wrapper function. It bootstraps the
// connection between your component and the Streamlit app, and handles
// passing arguments from Python -> Component.
//
// You don't need to edit withStreamlitConnection (but you're welcome to!).
export default withStreamlitConnection(MyComponent)
