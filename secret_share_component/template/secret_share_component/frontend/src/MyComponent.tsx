import {
  Streamlit,
  StreamlitComponentBase,
  withStreamlitConnection,
} from "streamlit-component-lib"
import React, { ReactNode } from "react"

interface State {
  prevInputData: any;
}

function secret_share(data: any) {
  var shares1 = new BigUint64Array(1);
  var shares2 = new BigUint64Array(1);
  var shares3 = new BigUint64Array(1);
  crypto.getRandomValues(shares1);
  crypto.getRandomValues(shares2);
  if (typeof (data) === 'string') {
    shares3[0] = 0n ^ shares1[0] ^ shares2[0];
    shares1[0] ^= BigInt(data)
  } else if (typeof (data === 'number')) {
    shares3[0] = 0n - shares1[0] - shares2[0];
    shares1[0] += BigInt(data)
  }
  return [shares1[0], shares2[0], shares3[0]]
}

function secret_share_arithmetic(_data: any, _replication_factor: any) {
  // makes sure _replication_factor > 2
  if (_replication_factor < 3) {
    throw new Error("Replication factor must be greater than 2");
  }

  var result_shares = new Int32Array(_replication_factor);
  crypto.getRandomValues(result_shares);
  result_shares[0] = Number(_data);
  for (var i = 1; i < _replication_factor; i++) {
    result_shares[0] -= result_shares[i];
  }

  return result_shares;
}

function secret_share_boolean(_data: any, _replication_factor: any) {
  // makes sure _replication_factor > 2
  if (_replication_factor < 3) {
    throw new Error("Replication factor must be greater than 2");
  }

  var result_shares = new Int32Array(_replication_factor);
  crypto.getRandomValues(result_shares);
  result_shares[0] = Number(_data);
  for (var i = 1; i < _replication_factor; i++) {
    result_shares[0] ^= result_shares[i];
  }

  return result_shares;
}

// Function that takes in the table schema, data and replication factor 
// and returns the secret shared data. The data is secret shared using the
// both the arithmetic and boolean secret sharing schemes. For each input column,
// we get _replication_factor output secret shared columns for arithmetic secret sharing
// and another _replication_factor output secret shared columns for boolean secret sharing.
// For example, for input column 'x' with replication factor 3, we get 6 output columns,
// named '[x]_1', '[x]_2', '[x]_3', 'x_1', 'x_2', 'x_3'.
// The first 3 columns with the square brackets are for boolean secret sharing.
// The next 3 columns are for arithmetic secret sharing.
// The output is a map representing the content of the resulting CSV file.
function secret_share_csv(_table_schema: any, _data: any, _replication_factor: any) {
  // Initialize the output data as a map of column names to secret shared data
  let output_data = new Map();
  let rows_number = _data[Object.keys(_data)[0]].length;

  // Iterate over all columns in the input data
  for (let column_name of _table_schema) {
    // create '[x]_i' and 'x_i' column names
    for (let i = 0; i < _replication_factor; i++) {
      output_data.set(`${column_name}_${i}`, new Int32Array(rows_number));
    }

    for (let i = 0; i < _replication_factor; i++) {
      output_data.set(`[${column_name}]_${i}`, new Int32Array(rows_number));
    }

    // iterate over rows in the column
    for (let j = 0; j < rows_number; j++) {
      let shares_1 = secret_share_arithmetic(_data[column_name][j], _replication_factor);
      for (let i = 0; i < _replication_factor; i++) {
        output_data.get(`${column_name}_${i}`)[j] = shares_1[i];
      }

      let shares_2 = secret_share_boolean(_data[column_name][j], _replication_factor);
      for (let i = 0; i < _replication_factor; i++) {
        output_data.get(`[${column_name}]_${i}`)[j] = shares_2[i];
      }
    }
  }
  // console.log("output_data", Object.fromEntries(output_data));
  console.log(JSON.stringify(Object.fromEntries(output_data), null, 2));
  return output_data;
}

class MyComponent extends StreamlitComponentBase<State> {
  public render = (): ReactNode => {
    return null // No visible UI component
  }

  // Trigger secret sharing on mount or whenever the component updates
  public componentDidMount(): void {
    console.log("Component did mount");
    this.executeSecretSharing()
  }

  public componentDidUpdate(): void {
    console.log("Component did update");
    // Compare the current data with the previous one
    // const prevData = this.props.args["_lastData"] || null
    const currentData = this.props.args["data"]

    this.executeSecretSharing()
    // Save the current data as _lastData to avoid re-processing
    this.props.args["_lastData"] = currentData
  }

  private executeSecretSharing = (): void => {
    const inputData = this.props.args["data"]
    if (!inputData) return

    console.log(JSON.stringify(inputData, null, 2));

    const outputData = secret_share_csv(inputData["schema"], inputData["data"], inputData["replication_factor"])
    // const plainOutputData = Object.fromEntries(
    //   Array.from(outputData, ([key, value]) => [key, Array.from(value)])
    // );
    const plainOutputData = Object.fromEntries(
      Array.from(outputData, ([key, value]) => [key, Array.from(value)])
    );
    console.log("output_data", Object.fromEntries(outputData));
    console.log("plainOutputData", plainOutputData);
    try {
      Streamlit.setComponentValue(plainOutputData);
    } catch (error) {
      console.error("Error sending data to Streamlit:", error);
    }
  }
}





// class MyComponent extends StreamlitComponentBase<State> {
//   public state: State = {
//     prevInputData: null,
//   };

//   // Custom method to handle updates
//   private handleInputChange(): void {
//     const inputData = this.props.args.data;

//     // Check if the input data has changed
//     if (JSON.stringify(this.state.prevInputData) !== JSON.stringify(inputData)) {
//       console.log("Input data changed:", JSON.stringify(inputData));

//       // Perform secret sharing and send result back to Streamlit
//       const outputData = secret_share_csv(inputData.schema, inputData.data, 3);
//       console.log("Sending back to Streamlit:", outputData);

//       Streamlit.setComponentValue(inputData);

//       // Update the previous input data in state
//       this.setState({ prevInputData: inputData });
//     }
//   }

//   public render(): null {
//     // Trigger input handling on each render
//     this.handleInputChange();

//     // This component has no visible UI
//     return null;
//   }
// }

export default withStreamlitConnection(MyComponent);

// interface State {
//   isFocused: boolean
// }

// Function that takes in the table schema, data and replication factor 
// and returns the secret shared data. The data is secret shared using the
// both the arithmetic and boolean secret sharing schemes. For each input column,
// we get _replication_factor output secret shared columns for arithmetic secret sharing
// and another _replication_factor output secret shared columns for boolean secret sharing.
// For example, for input column 'x' with replication factor 3, we get 6 output columns,
// named '[x]_1', '[x]_2', '[x]_3', 'x_1', 'x_2', 'x_3'.
// The first 3 columns with the square brackets are for boolean secret sharing.
// The next 3 columns are for arithmetic secret sharing.
// The output is a map representing the content of the resulting CSV file.

// class MyComponent extends StreamlitComponentBase<State> {
//   public state = { isFocused: false }

//   public render = (): ReactNode => {

//     const { theme } = this.props
//     const style: React.CSSProperties = {}

//     if (theme) {
//       const borderStyling = `1px solid ${this.state.isFocused ? theme.primaryColor : "gray"
//         }`;
//       style.border = borderStyling;
//       style.outline = borderStyling;
//     }


//     return (
//       <span>
//         <button
//           style={style}
//           onClick={this.onClicked}
//           disabled={this.props.disabled}
//           onFocus={this._onFocus}
//           onBlur={this._onBlur}
//         >
//           Generate Secret Shares
//         </button>
//       </span>
//     )
//   }

//   private onClicked = (): void => {
//     // Example input data for secret sharing
//     const inputData = this.props.args["data"]

//     console.log("inputData", JSON.stringify(inputData, null, 2));
//     const outputData = secret_share_csv(inputData["schema"], inputData["data"], inputData["replication_factor"])

//     // Send the shares back to the Streamlit app
//     Streamlit.setComponentValue(outputData)
//   }

//   private _onFocus = (): void => {
//     this.setState({ isFocused: true })
//   }

//   private _onBlur = (): void => {
//     this.setState({ isFocused: false })
//   }
// }

// export default withStreamlitConnection(MyComponent)