import React, { Component } from "react"
import { withStyles } from "@material-ui/core/styles"
import Authenticate from "./authentication/authenticate"

const styles = theme => ({})

class Main extends Component {
  state = {
    token: null
  }

  render() {
    const { token } = this.state

    if (!token) {
      return (
        <Authenticate
          onAuthenticated={(token, currentUser) =>
            this.setState({ token, currentUser })
          }
        />
      )
    }

    return (
      <div>
        <p>This is the login screen</p>
      </div>
    )
  }
}

export default withStyles(styles)(Main)
