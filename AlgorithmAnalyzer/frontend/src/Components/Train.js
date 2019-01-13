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

class Train extends Component {
    constructor(props) {
        super(props);
        this.state = {
            algorithm: "", // the name of currently selected algorithm
            description: "",
            parameters: {}, // the parameter name.{descriptions,values}
            parameter_values: {}, //values of parameters sent to server, name.{value} object
            status: "", // the status of train tesponse, if the training started or an error occured
            // TODO(mikra): add server events informing about training status
        }
    }

    handleChangeAlgorithm = event => {
        this.setState({ [event.target.name]: event.target.value });
        if(event.target.value === ""){
            this.setState({
                parameters: {},
                parameter_values: {},
                status: "",
                description: ""
            })
        } else {
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
            .get(`http://localhost:5000/algorithms/description/${algorithm}`)
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
            .get(`http://localhost:5000/algorithm/parameters/${algorithm}`)
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
        this.setState({status: ""});
        if(this.state.algorithm === "") return;
        axios.post(`http://localhost:5000/algorithm/train/${this.state.algorithm}`, {
            parameters: this.state.parameter_values
        }).then(res => {
            console.log("Rozpoczęto trenowanie");
            this.setState({
                status: res.data
            })
            console.log(res)
        }).catch(err => {
            console.log(err.response.data)
        })
    };
    renderParameter  = name => {
        console.log(name);
        let params = this.state.parameters[name];
        let val = this.state.parameter_values[name];
        return (
        <tr style={{borderBottom: "1px solid #fff"}} key={name /* needed to mitigate a warning */}>
            <td><Typography variant="body2" style={{color: "#fff"}} gutterBottom> {name}</Typography></td>
            <td style={{borderLeft: "2px solid #fff"}}><Typography variant="body2" style={{color: "#fff"}} gutterBottom> {params.description} </Typography></td>
            <td style={{borderLeft: "2px solid #fff"}}>
                <Select
                                    value={val}
                                    onChange={event => this.handleChangeParameter(event, name)}
                                    inputProps={{
                                        name: 'algorithm',
                                    }}
                                >
                                {params.values.map((value) => <MenuItem key={value} value={value}>{value}</MenuItem>)}
                </Select>
            </td>
        </tr>
        )
    };

    render(){
        return(
            <Paper style={{ margin: 20,backgroundColor: 'rgba(0, 0, 0, .6)'}}>
                <div
				    style={{display: 'flex', flexDirection: 'row'}}
			        >
                    <div
                        style={{
                            backgroundColor: 'rgba(0, 0, 0, .8)',
                            width: '100%',
                            margin: 20,
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
                            <Typography variant="title" style={{color: "#fff"}} gutterBottom>
                                Parametry algorytmu
                            </Typography>
                            <table style={{width: "100%", textAlign: "center", tableLayout: "fixed", borderCollapse: "collapse"}}><tbody>
                            <tr style={{borderBottom: "1px solid #fff"}}>
                                <td><Typography variant="subheading" style={{color: "#fff"}} gutterBottom>Nazwa</Typography></td>
                                <td><Typography variant="subheading" style={{color: "#fff"}} gutterBottom>Opis</Typography></td>
                                <td><Typography variant="subheading" style={{color: "#fff"}} gutterBottom>Wartość</Typography></td>
                            </tr>
                            {Object.keys(this.state.parameters).map( this.renderParameter )}
                            </tbody></table>
                            </div>
                        )}
                </Grid>
                </div>
              </div>
            </Paper>
        )
    }
}
Train.propTypes = {
    algorithmList: PropTypes.array
  };
export default Train