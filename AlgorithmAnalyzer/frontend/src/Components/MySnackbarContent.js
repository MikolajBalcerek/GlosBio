import React from 'react';
import PropTypes from 'prop-types';
import classNames from 'classnames';
import Button from '@material-ui/core/Button';
import CheckCircleIcon from '@material-ui/icons/CheckCircle';
import ErrorIcon from '@material-ui/icons/Error';
import InfoIcon from '@material-ui/icons/Info';
import CloseIcon from '@material-ui/icons/Close';
import green from '@material-ui/core/colors/green';
import amber from '@material-ui/core/colors/amber';
import IconButton from '@material-ui/core/IconButton';
import Snackbar from '@material-ui/core/Snackbar';
import SnackbarContent from '@material-ui/core/SnackbarContent';
import WarningIcon from '@material-ui/icons/Warning';
import { withStyles } from '@material-ui/core/styles';

const variantIcon = {
  success: CheckCircleIcon,
  warning: WarningIcon,
  error: ErrorIcon,
  info: InfoIcon,
};

const styles1 = theme => ({
  success: {
    backgroundColor: green[600],
  },
  error: {
    backgroundColor: theme.palette.error.dark,
  },
  info: {
    backgroundColor: theme.palette.primary.dark,
  },
  warning: {
    backgroundColor: amber[700],
  },
  icon: {
    fontSize: 20,
  },
  iconVariant: {
    opacity: 0.9,
    marginRight: theme.spacing.unit,
  },
  message: {
    display: 'flex',
    alignItems: 'center',
  },
});

function MySnackbarContent(props) {
  const { classes, className, message, onClose, variant, ...other } = props;
  const Icon = variantIcon[variant];

  return (
    <SnackbarContent
      className={classNames(classes[variant], className)}
      aria-describedby="client-snackbar"
      message={
        <span id="client-snackbar" className={classes.message}>
          <Icon className={classNames(classes.icon, classes.iconVariant)} />
          {message}
        </span>
      }
      action={[
        <IconButton
          key="close"
          aria-label="Close"
          color="inherit"
          className={classes.close}
          onClick={onClose}
        >
          <CloseIcon className={classes.icon} />
        </IconButton>,
      ]}
      {...other}
    />
  );
}

MySnackbarContent.propTypes = {
  openErrorNoAudio: PropTypes.bool,
  openErrorNoUser: PropTypes.bool,
  openSuccess: PropTypes.bool,
  openErrorSave: PropTypes.bool,
  SnackbarHandleClose: PropTypes.func,
  classes: PropTypes.object.isRequired,
  className: PropTypes.string,
  message: PropTypes.node,
  onClose: PropTypes.func,
  openUploadSuccess: PropTypes.bool,
  openUploadError: PropTypes.bool,
  openErrorFileType: PropTypes.bool,
  openErrorFileSize: PropTypes.bool,
  variant: PropTypes.oneOf(['success', 'warning', 'error', 'info']).isRequired,
};

const MySnackbarContentWrapper = withStyles(styles1)(MySnackbarContent);

const styles2 = theme => ({
  margin: {
    margin: theme.spacing.unit,
  },
});

class CustomizedSnackbars extends React.Component {
  state = {
    open: false,
  };

  handleClick = () => {
    this.setState({ open: true });
  };

  handleClose = (event, reason) => {
    if (reason === 'clickaway') {
      return;
    }

    this.setState({ openErrorNoAudio: false, openSuccess: false, openErrorNoUser: false  });
  };

  render() {
    const { classes } = this.props;

    return (
      <div>
        <Snackbar
          anchorOrigin={{
            vertical: 'bottom',
            horizontal: 'left',
          }}
          open={this.props.openSuccess}
          autoHideDuration={2000}
          onClose={this.props.SnackbarHandleClose()}
        >
          <MySnackbarContentWrapper
            onClose={this.props.SnackbarHandleClose()}
            variant="success"
            message="Plik zapisano poprawnie!"
          />
        </Snackbar>
        <Snackbar
          anchorOrigin={{
            vertical: 'bottom',
            horizontal: 'left',
          }}
          open={this.props.openUploadSuccess}
          autoHideDuration={2000}
          onClose={this.props.SnackbarHandleClose()}
        >
          <MySnackbarContentWrapper
            onClose={this.props.SnackbarHandleClose()}
            variant="success"
            message="Plik wczytano poprawnie!"
          />
        </Snackbar>
        <Snackbar
          anchorOrigin={{
            vertical: 'bottom',
            horizontal: 'left',
          }}
          open={this.props.openErrorNoAudio}
          autoHideDuration={2000}
          onClose={this.props.SnackbarHandleClose()}
        >
         <MySnackbarContentWrapper
          onClose={this.props.SnackbarHandleClose()}
          variant="error"
          className={classes.margin}
          message="Nie można zapisać pliku, nie został nagrany"
        />
        </Snackbar>
        <Snackbar
          anchorOrigin={{
            vertical: 'bottom',
            horizontal: 'left',
          }}
          open={this.props.openErrorFileType}
          autoHideDuration={2000}
          onClose={this.props.SnackbarHandleClose()}
        >
         <MySnackbarContentWrapper
          onClose={this.props.SnackbarHandleClose()}
          variant="error"
          className={classes.margin}
          message="Format pliku jest niepoprawny"
        />
        </Snackbar>
        <Snackbar
          anchorOrigin={{
            vertical: 'bottom',
            horizontal: 'left',
          }}
          open={this.props.openErrorFileSize}
          autoHideDuration={2000}
          onClose={this.props.SnackbarHandleClose()}
        >
         <MySnackbarContentWrapper
          onClose={this.props.SnackbarHandleClose()}
          variant="error"
          className={classes.margin}
          message="Plik jest zbyt duży"
        />
        </Snackbar>
        <Snackbar
          anchorOrigin={{
            vertical: 'bottom',
            horizontal: 'left',
          }}
          open={this.props.openUploadError}
          autoHideDuration={2000}
          onClose={this.props.SnackbarHandleClose()}
        >
         <MySnackbarContentWrapper
          onClose={this.props.SnackbarHandleClose()}
          variant="error"
          className={classes.margin}
          message="Nie można wczytać pliku"
        />
        </Snackbar>
        <Snackbar
          anchorOrigin={{
            vertical: 'bottom',
            horizontal: 'left',
          }}
          open={this.props.openErrorNoUser}
          autoHideDuration={2000}
          onClose={this.props.SnackbarHandleClose()}
        >
         <MySnackbarContentWrapper
          onClose={this.props.SnackbarHandleClose()}
          variant="error"
          className={classes.margin}
          message="Nie można zapisać pliku, podaj imię i nazwisko"
        />
        </Snackbar>
        <Snackbar
          anchorOrigin={{
            vertical: 'bottom',
            horizontal: 'left',
          }}
          open={this.props.openErrorSave}
          autoHideDuration={2000}
          onClose={this.props.SnackbarHandleClose()}
        >
         <MySnackbarContentWrapper
          onClose={this.props.SnackbarHandleClose()}
          variant="error"
          className={classes.margin}
          message="Nie można zapisać pliku, błąd zapisu"
        />
        </Snackbar>
      </div>
    );
  }
}

CustomizedSnackbars.propTypes = {
  classes: PropTypes.object.isRequired,
};

export default withStyles(styles2)(CustomizedSnackbars);