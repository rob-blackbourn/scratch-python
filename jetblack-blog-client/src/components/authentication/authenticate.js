import React, { Component } from "react"
import PropTypes from "prop-types"
import { withStyles } from "@material-ui/core/styles"
import Login from "./login"
import Register from "./register"

const styles = theme => ({
  container: {}
})

class Authenticate extends Component {
  state = {
    mode: "login"
  }

  handleToken = (token, onAuthenticated) => {
    const query = "query { currentUser { roles } }"

    fetch("http://localhost:8080/graphql", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        Accept: "application/json",
        Authorization: `Bearer ${token}`
      },
      body: JSON.stringify({
        query
      })
    })
      .then(response => response.json())
      .then(response => {
        console.log(response)
        if (response.errors) {
          this.setState({ error: "Invalid username or password" })
          console.log("Failed")
        } else {
          onAuthenticated(token, response.data.currentUser)
        }
      })
      .catch(error => {
        this.setState({ error: "Failed to communicate with the server" })
      })
  }

  render() {
    const { onAuthenticated, classes } = this.props
    const { mode } = this.state

    if (mode === "login") {
      return (
        <Login
          className={classes.container}
          onToken={token => this.handleToken(token, onAuthenticated)}
          onModeChanged={mode => this.setState({ mode })}
        />
      )
    } else {
      return (
        <Register
          className={classes.container}
          onToken={token => this.handleToken(token, onAuthenticated)}
          onModeChanged={mode => this.setState({ mode })}
        />
      )
    }
  }
}

Authenticate.propTypes = {
  classes: PropTypes.object,
  onAuthenticated: PropTypes.func.isRequired
}

export default withStyles(styles)(Authenticate)
