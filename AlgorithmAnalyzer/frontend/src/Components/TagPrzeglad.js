import React, { Component } from 'react'
import IconButton from '@material-ui/core/IconButton';
import DeleteIcon from '@material-ui/icons/Delete';
import InputLabel from '@material-ui/core/InputLabel';
import FormControl from '@material-ui/core/FormControl';
import Select from '@material-ui/core/Select';
import MenuItem from '@material-ui/core/MenuItem';
import Button from '@material-ui/core/Button';
import Table from '@material-ui/core/Table';
import TableBody from '@material-ui/core/TableBody';
import TableCell from '@material-ui/core/TableCell';
import TableRow from '@material-ui/core/TableRow';
export default class TagPrzeglad extends Component {
    render(){
        return(
            <div>
            <FormControl style={{ minWidth: 180,width: '100%', paddingRight: 10 }}>
                <div style={{display: 'flex', justifyContent:'space-between'}}>
                    <InputLabel>Wybierz tag</InputLabel>
                        <Select
                            value={this.props.tag}
                            onChange={(e)=>this.props.handleChangeTag(e)}
                            style={{width: 200}}
                            inputProps={{
                            name: 'tag',
                            }}
                        >
                            <MenuItem value="">
                            <em>None</em>
                            </MenuItem>
                            {this.props.tagNameList && this.props.tagNameList.map((user, id) => <MenuItem key={id} value={id}>{user}</MenuItem>)}
                        </Select>
                        <IconButton 
                            aria-label="Usuń" 
                            style={{backgroundColor: '#550000'}}
                            onClick={()=>this.props.deleteTag()}
                            disabled={this.props.tag === ''}
                            >
                            <DeleteIcon />
                        </IconButton>
                    </div>
                </FormControl>
                    <div style={{height: 220, overflow: 'auto'}}>
                        <Table>
                            <TableBody>
                                {this.props.tagValuesList.length > 0 &&this.props.tagValuesList.map(
                                    tagValue=>
                                    <TableRow>
                                        <TableCell style={{textAlign: 'center'}}>{tagValue}</TableCell>
                                    </TableRow>
                                        )}
                            </TableBody>
                        </Table>
                    </div>
                    <Button 
                        onClick={()=>this.props.handleOpenTags()}
                        color='primary' 
                        style={{marginTop: 20}}
                        variant="contained">
                        Dodaj nowy tag
                    </Button>
            </div>
        )
    }
}