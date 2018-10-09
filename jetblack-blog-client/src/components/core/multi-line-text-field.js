import React, { Component, Fragment } from "react"
import PropTypes from "prop-types"
import { withStyles } from "@material-ui/core/styles"
import Grid from "@material-ui/core/Grid"
import TextField from "@material-ui/core/TextField"
import Button from "@material-ui/core/Button"

const styles = theme => ({
  textField: {
    marginLeft: theme.spacing.unit,
    marginRight: theme.spacing.unit,
    width: 300
  },
  buttons: {
    width: 50
  }
})

class MultiLineTextField extends Component {
  render() {
    const {
      classes,
      lines,
      onChange,
      label,
      addLabel,
      removeLabel
    } = this.props

    return (
      <Grid container>
        {lines.map((line, index) => {
          return (
            <Fragment>
              <Grid item xs={11}>
                <TextField
                  className={classes.textField}
                  label={label}
                  value={line}
                  margin="normal"
                  onChange={event =>
                    onChange([
                      ...lines.slice(0, index),
                      event.target.value,
                      ...lines.slice(index + 1)
                    ])
                  }
                />
              </Grid>
              <Grid item xs={1}>
                {index < lines.length - 1 ? null : (
                  <Fragment className={classes.buttons}>
                    <Button onClick={() => onChange([...lines, ""])}>
                      {addLabel}
                    </Button>
                    {lines.length <= 1 ? null : (
                      <Button onClick={() => onChange(lines.slice(0, -1))}>
                        {removeLabel}
                      </Button>
                    )}
                  </Fragment>
                )}
              </Grid>
            </Fragment>
          )
        })}
      </Grid>
    )
  }
}

MultiLineTextField.propTypes = {
  classes: PropTypes.object,
  lines: PropTypes.arrayOf(PropTypes.string).isRequired,
  onChange: PropTypes.func.isRequired,
  label: PropTypes.string.isRequired,
  addLabel: PropTypes.any.isRequired,
  removeLabel: PropTypes.any.isRequired
}

MultiLineTextField.defaultProps = {
  addLabel: "Add",
  removeLabel: "Remove"
}
export default withStyles(styles)(MultiLineTextField)
