import React, { Component } from 'react'
import Paper from '@material-ui/core/Paper';
import MenuItem from '@material-ui/core/MenuItem';
import FormControl from '@material-ui/core/FormControl';
import Select from '@material-ui/core/Select';
import InputLabel from '@material-ui/core/InputLabel';
import Typography from '@material-ui/core/Typography';
import Grid from '@material-ui/core/Grid';
import Button from '@material-ui/core/Button';
import PropTypes from 'prop-types';
import axios from 'axios';
import api_config from '../api_config.json'
import Table from '@material-ui/core/Table';
import TableBody from '@material-ui/core/TableBody';
import TableCell from '@material-ui/core/TableCell';
import TableHead from '@material-ui/core/TableHead';
import TableRow from '@material-ui/core/TableRow';
import Fade from '@material-ui/core/Fade';
import { withSnackbar } from 'notistack'
import LinearProgress from '@material-ui/core/LinearProgress';
import IconButton from '@material-ui/core/IconButton';
import DeleteIcon from '@material-ui/icons/Delete';

class Train extends Component {
    constructor(props) {
        super(props);
        this.state = {
            algorithm: "", // the name of currently selected algorithm
            description: "", // the description of the algorithm
            parameters: {}, // the parameter name.{descriptions,values}
            parameter_values: {}, //values of parameters sent to server, name.{value} object
            status: "", // the status of train tesponse, if the training started or an error occured
            modelTable: []
        }
    }

    handleClickVariant(text, variant){
        // variant could be success, error, warning or info
        this.props.enqueueSnackbar(text, { variant });
      }
    handleChangeAlgorithm = event => {
        this.setState({
            [event.target.name]: event.target.value,
            parameters: {},
            parameter_values: {},
            status: "",
            description: ""
        });
        if(event.target.value !== ""){
            this.setState({status: ""});
            this.getAlgorithmDecription(event.target.value);
            this.getAlgorithmParameters(event.target.value);
        }
      };

      handleChangeParameter = (event, name) => {
        let params = this.state.parameter_values;
        console.log(name)
        params[name] = event.target.value;
        this.setState({
            parameter_values: params
        })
        console.log(params);
      };

    getAlgorithmDecription = algorithm => {
        var self = this;
        axios
            .get(api_config.usePath + `/algorithms/description/${algorithm}`)
            .then(function(response) {
                let description = response.data;
                console.log(description);
                self.setState({description: description});
            })
            .catch(function(error) {
                console.log(error);
            })
    };

    getAlgorithmParameters = algorithm => {
        var self = this;
        axios
            .get(api_config.usePath + `/algorithms/parameters/${algorithm}`)
            .then(function(response) {
                let params = response.data.parameters;
                let param_vals = {}
                Object.keys(params).map((key, i) => {
                    param_vals[key] = params[key].values[0];
                    return params[key]; // return is needed to omit worning with map
                });
				self.setState({parameters: params, parameter_values: param_vals});
                console.log(self.state.parameters);
            })
            .catch(function(error) {
                console.log(error);
			})
    };
    trainButtonClick = () => {
        if(this.state.algorithm === "") return;
        axios.post(api_config.usePath + `/algorithms/train/${this.state.algorithm}`, {
            parameters: this.state.parameter_values
        }).then(res => {
            this.handleClickVariant(res.data.message, 'success')
        }).catch(err => {
            this.handleClickVariant(err, 'error')

        })
    };
    
    renderParameter  = name => {
        console.log(name);
        let params = this.state.parameters[name];
        let val = this.state.parameter_values[name];
        return (
            <TableRow key={name}>
                <TableCell>{name}</TableCell>
                <TableCell>{params.description}</TableCell>
                <TableCell>
                    <Select
                        value={val}
                        onChange={event => this.handleChangeParameter(event, name)}
                        inputProps={{
                            name: 'algorithm',
                            }}
                    >
                        {params.values.map((value) => <MenuItem key={value} value={value}>{value}</MenuItem>)}
                    </Select>
                </TableCell>
            </TableRow>
        )
    };

    render(){
        return(
            <Fade in={true}>
            <Paper style={{ margin: 20,backgroundColor: 'rgba(0, 0, 0, .6)'}}>
                <div
				    style={{display: 'flex', flexDirection: 'row'}}
			        >
                    <div
                        style={{
                            backgroundColor: 'rgba(0, 0, 0, .8)',
                            width: '100%',
                            borderRadius: 5,
                            textAlign: 'center',
                            display: 'flex',
                            flexDirection: 'column',
                            padding: 15,
                            border: '3px solid rgba(120, 0, 0, .6)',
                            alignItems: 'center',
                            justifyContent: 'center'
                        }}
                    >
                    <Grid item xs={12} style={{display: 'flex',  justifyContent:'space-around', alignItems:'center', width: '100%'}}>
                        <FormControl style={{ minWidth: 200, paddingRight: 10 }}>
                            <InputLabel >Wybierz algorytm</InputLabel>
                            <Select
                                value={this.state.algorithm}
                                onChange={this.handleChangeAlgorithm}
                                inputProps={{
                                name: 'algorithm',
                                }}
                            >
                            <MenuItem value="">
                                <em>None</em>
                            </MenuItem>
                            {this.props.algorithmList && this.props.algorithmList.map((name) => <MenuItem key={name} value={name}>{name}</MenuItem>)}
                            </Select>
                        </FormControl>
                        <Button onClick={this.trainButtonClick} color='primary' variant="contained">Trenuj</Button>
                    </Grid>
                    <Grid item xs={12} style={{display: 'flex', flexDirection: 'column', justifyContent:'space-around', alignItems:'center', width: '100%', marginTop: 30, minHeight: 200 }}>
                        {this.state.status && <Typography variant="headline" gutterBottom> {this.state.status} </Typography>}
                        {this.state.algorithm !== "" && this.state.description !== "" && this.state.description &&
                            <div>
                            <Typography variant="title" style={{colot: "#fff"}} gutterBottom> Opis algorytmu </Typography>
                            <Typography variant="subheading" style={{colot: "#fff"}} gutterBottom> {this.state.description} </Typography>
                            </div>
                        }
                        {this.state.algorithm !== "" && Object.keys(this.state.parameters).length !== 0 && (
                            <div>
                                <div style={{display: 'flex'}}>
                                    <div style={{width: '100%'}}>
                                        <Typography variant="title" style={{color: "#fff"}} gutterBottom>
                                            Parametry algorytmu
                                        </Typography>
                                        <Table style={{width: '100%'}}>
                                            <TableHead>
                                                <TableRow>
                                                    <TableCell>Nazwa</TableCell>
                                                    <TableCell>Opis</TableCell>
                                                    <TableCell>Wartość</TableCell>
                                                </TableRow>
                                            </TableHead>
                                            <TableBody>
                                                {Object.keys(this.state.parameters).map( this.renderParameter )}
                                            </TableBody>
                                        </Table>
                                    </div>
                                </div>
                            </div>
                        )}
                </Grid>
                </div>
              </div>
            </Paper>
            </Fade>
        )
    }
}
Train.propTypes = {
    enqueueSnackbar: PropTypes.func.isRequired,
    algorithmList: PropTypes.array
  };
export default  withSnackbar(Train)