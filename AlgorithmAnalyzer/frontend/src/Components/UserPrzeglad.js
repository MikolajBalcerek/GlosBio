import React, { Component } from 'react'
import Table from '@material-ui/core/Table';
import TableBody from '@material-ui/core/TableBody';
import TableCell from '@material-ui/core/TableCell';
import TableHead from '@material-ui/core/TableHead';
import TableRow from '@material-ui/core/TableRow';
import IconButton from '@material-ui/core/IconButton';
import DeleteIcon from '@material-ui/icons/Delete';
import InputLabel from '@material-ui/core/InputLabel';
import FormLabel from '@material-ui/core/FormLabel';
import FormControl from '@material-ui/core/FormControl';
import Select from '@material-ui/core/Select';
import Tabs from '@material-ui/core/Tabs';
import Tab from '@material-ui/core/Tab';
import MenuItem from '@material-ui/core/MenuItem';
import Button from '@material-ui/core/Button';
import { PieChart, 
    Pie, 
    Sector, 
    BarChart, 
    Bar, 
    XAxis, 
    YAxis, 
    CartesianGrid, 
    Tooltip,
    Legend,
    Cell
   } from 'recharts'
export default class UserPrzeglad extends Component {
    render(){
        return(
            <div>
            <FormControl style={{ minWidth: 180,width: '100%', paddingRight: 10 }}>
                <div style={{display: 'flex', justifyContent:'space-between'}}>
                    <InputLabel>Wybierz użytkownika</InputLabel>
                        <Select
                            value={this.props.user}
                            onChange={(e)=>this.props.handleChangeUser(e)}
                            style={{width: 200}}
                            inputProps={{
                            name: 'user',
                            }}
                        >
                            <MenuItem value="">
                            <em>None</em>
                            </MenuItem>
                            {this.props.userList && this.props.userList.map((user, id) => <MenuItem key={id} value={id}>{user}</MenuItem>)}
                        </Select>
                        <IconButton aria-label="Usuń" style={{backgroundColor: '#550000'}}>
                            <DeleteIcon />
                        </IconButton>
                    </div>
                </FormControl>
                <Tabs
                    value={this.props.userValue}
                    onChange={(e,v)=>this.props.handleChangeUserTab(e, v)}
                    indicatorColor="primary"
                    textColor="primary"
                    fixed
                    style={{backgroundColor: 'black', marginBottom: 10, width: 300}}
                    >
                    <Tab  label='Typ' />
                    <Tab  label='Tagi' />
                </Tabs>
                    <div style={{height: 220}}>
                        {(this.props.userTagCount.length !== 0 && this.props.userValue === 0) &&
                                    <BarChart width={280} height={180} data={this.props.userTagCount}
                                            margin={{top: 5, right: 30, left: 20, bottom: 5}}>
                                        <CartesianGrid strokeDasharray="3 3"/>
                                        <XAxis dataKey="name"/>
                                        <YAxis/>
                                        <Tooltip/>
                                        <Legend />
                                        <Bar dataKey="value">
                                        {
                                            this.props.userTagCount.map((entry, index) => (
                                            <Cell key={`cell-${index}`} fill={`rgb(${120+(100 +index*30)%135}, 10, 20)`}/>
                                            ))
                                        }
                                        </Bar>
                                    </BarChart>}
                        {(this.props.userValue === 1 && this.props.userList[this.props.user]) && <div style={{ margin: 20, padding: 10, height: 190, 
                                    overflow: 'auto'}}>
                        <div style={{
                                    height: 180, 
                                    overflow: 'auto'}}>
                            <Table>
                                <TableHead>
                                <TableRow>
                                    <TableCell>Nazwa</TableCell>
                                    <TableCell align="right">Wartość</TableCell>
                                </TableRow>
                                </TableHead>
                                <TableBody>
                                {Object.keys(this.props.userTags).length > 0 && Object.keys(this.props.userTags).map((tag, i) => {
                                    return (
                                    <TableRow key={i}>
                                        <TableCell component="th" scope="row">
                                        {tag}
                                        </TableCell>
                                        <TableCell align="right">
                                        {this.props.userTags[tag]}
                                        </TableCell>
                                    </TableRow>
                                    );
                                })}
                                <TableRow>
                                        <TableCell component="th" scope="row">
                                            <Select
                                                value={this.props.name}
                                                onChange={(e)=>this.props.handleChangeName(e)}
                                                inputProps={{
                                                name: 'name',
                                                }}
                                            >
                                            <MenuItem value="">
                                                <em>None</em>
                                            </MenuItem>
                                            {this.props.tagNameList && this.props.tagNameList.map(
                                                (name, id) => 
                                                Object.keys(this.props.userTags).indexOf(name) === -1 && <MenuItem key={id} value={id}>{name}</MenuItem>
                                                )
                                                }
                                            </Select>
                                        </TableCell>
                                        <TableCell align="right">
                                            <Select
                                                value={this.props.tagValue}
                                                onChange={(e)=>this.props.handleChangeTagValue(e)}
                                                inputProps={{
                                                name: 'tagValue',
                                                }}
                                            >
                                            <MenuItem value="">
                                                <em>None</em>
                                            </MenuItem>
                                            {this.props.tagValuesList && this.props.tagValuesList.map((val, id) => <MenuItem key={id} value={id}>{val}</MenuItem>)}
                                            </Select>
                                        </TableCell>
                                    </TableRow>
                                </TableBody>
                            </Table>
                        </div>
                        <div style={{display: 'flex'}}>
                            <Button 
                                variant="contained" 
                                onClick={()=>this.props.addTagToUser()} 
                                style={{margin: 30}}
                                disabled={!(this.props.tagValue || this.props.tagValue === 0)}
                                color='primary'
                                >
                                Przypisz tag
                            </Button>
                        </div>
                    </div>}
                </div>
            </div>
        )
    }
}