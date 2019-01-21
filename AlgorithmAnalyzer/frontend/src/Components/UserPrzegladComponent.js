import React, { Component } from 'react'
import MenuItem from '@material-ui/core/MenuItem';
import FormControl from '@material-ui/core/FormControl';
import Select from '@material-ui/core/Select';
import InputLabel from '@material-ui/core/InputLabel';
import Typography from '@material-ui/core/Typography';
import Grid from '@material-ui/core/Grid';
import Button from '@material-ui/core/Button';
import FormLabel from '@material-ui/core/FormLabel';
import RadioGroup from '@material-ui/core/RadioGroup';
import FormControlLabel from '@material-ui/core/FormControlLabel';
import Radio from '@material-ui/core/Radio';
import AudioSpectrum from "react-audio-spectrum"
import Tabs from '@material-ui/core/Tabs';
import Tab from '@material-ui/core/Tab';
import IconButton from '@material-ui/core/IconButton';
import DeleteIcon from '@material-ui/icons/Delete';

export default class UserPrzegladComponent extends Component {
    render(){
        return(
            <div>
                {this.props.userList[this.props.user] &&
                <div>
                    <Grid 
                        item 
                        xs={12} 
                        style={{
                            display: 'flex',  
                            justifyContent:'space-around', 
                            alignItems:'center', 
                            width: '100%'
                            }}>
                    <FormControl component="fieldset">
                        <FormLabel component="legend">Wybierz typ nagrania:</FormLabel>
                                    <RadioGroup
                                        value={this.props.type}
                                        onChange={(e)=>this.props.handleTypeChange(e)}
                                        style={{flexDirection: 'row'}}
                                    >
                                        <FormControlLabel value="train" control={<Radio />} label="Trenowanie" />
                                        <FormControlLabel value="test" control={<Radio />} label="Test" />
                                    </RadioGroup>
                                </FormControl>
                    <FormControl style={{ minWidth: 200, paddingRight: 10 }}>
                            <InputLabel >Wybierz próbkę</InputLabel>
                            <Select
                                value={this.props.sound}
                                onChange={(e)=>this.props.handleChangeSound(e)}
                                inputProps={{
                                name: 'sound'
                                }}
                            >
                            <MenuItem value=""/>
                            {this.props.userSounds && this.props.userSounds.map((sound, id) => <MenuItem key={id} value={id}>{sound}</MenuItem>)}
                        </Select>
                    </FormControl>
                        <Button 
                            onClick={()=>this.props.getSound()} 
                            color='primary' 
                            disabled={this.props.sound === ''}
                            variant="contained">
                            Załaduj próbkę
                        </Button>
                        <IconButton 
                            aria-label="Usuń" 
                            style={{backgroundColor: '#550000'}} 
                            onClick={()=>this.props.deleteUserSound()}
                            disabled={this.props.sound === ''}
                            >
                            <DeleteIcon />
                        </IconButton>
                    </Grid>
                    <Grid 
                        item 
                        xs={12} 
                        style={{
                            display: 'flex',  
                            justifyContent:'space-around', 
                            alignItems:'center', 
                            width: '100%', 
                            marginTop: 30, 
                            minHeight: 280 
                        }}> 
                    <div>
                    <audio id="audio-element"
                                src={this.props.url}
                                controls
                                >
                            </audio>
                            <AudioSpectrum
                                id="audio-canvas"
                                height={200}
                                width={280}
                                audioId={'audio-element'}
                                capColor={'red'}
                                capHeight={2}
                                meterWidth={2}
                                meterCount={512}
                                meterColor={[
                                    {stop: 0, color: '#f00'},
                                    {stop: 0.5, color: '#0CD7FD'},
                                    {stop: 1, color: 'red'}
                                ]}
                                gap={4}
                                />
                                </div>
                            <div > 
                                <Tabs
                                    value={this.props.value}
                                    onChange={(e, v)=>this.props.handleChange(e,v)}
                                    indicatorColor="primary"
                                    textColor="primary"
                                    fixed
                                    style={{backgroundColor: 'black', marginBottom: 10, width: 320}}
                                    >
                                        <Tab  label='Mfcc' />
                                        <Tab  label='Spektrogram' />
                                    </Tabs>
                                {(this.props.mfcc && this.props.value === 0) &&<Button onClick={()=>this.props.handleOpenMfcc()}>
                                <img 
                                    src={this.props.mfcc} 
                                    style={{
                                        width:250, backgroundColor: 'white', borderRadius: 10
                                        }} 
                                        />
                                </Button>}
                                {(this.props.spectrogram && this.props.value === 1) &&<Button onClick={()=>this.props.handleOpenSpectrogram()}>
                                <img 
                                    src={this.props.spectrogram} 
                                    style={{
                                        width:250, backgroundColor: 'white', borderRadius: 10
                                        }} 
                                        />
                                </Button>}
                            </div>
                    </Grid>
                </div>}
            </div>
        )
    }
}