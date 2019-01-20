import React, { Component } from 'react'
import logo from "../img/logo.png";
import logo2 from "../img/logo2.png";
import Button from '@material-ui/core/Button';
export default class MiddleBar extends Component {
    state = {
        isLogo: false
    }
    setLogo=()=>{
        console.log(this.state.isLogo)
        this.setState({
            isLogo: !this.state.isLogo
        })
    }

    render(){
        const styles ={
            button: {
                fontSize: '30px',
                color: '#fff',
                textShadow: '0 0 5px #fff, 0 0 10px #fff, 0 0 20px #3333ff, 0 0 30px #3333ff, 0 0 40px #3333ff, 0 0 55px #3333ff, 0 0 75px #3333ff',
                border: 0
            },
            buttonHidden: {
                fontSize: '30px',
                color: '#fff',
                textShadow: '0 0 5px #fff, 0 0 10px #fff, 0 0 20px #000, 0 0 30px #000, 0 0 40px #000, 0 0 55px #000, 0 0 75px #000',
                border: 0
            }
        }
        return(
            <div style={{display: 'flex', alignItems: 'center', justifyContent: 'space-around'}}>
                <img
                    onMouseEnter={this.setLogo}
                    onMouseLeave={this.setLogo}
                    src={this.state.isLogo ? logo2 : logo}
                    style={{width: 120, height: 120, cursor: 'pointer'}}
                    onClick={()=>this.props.handleChange1()}
                />
                <Button
                    variant="outlined"
                    style={this.props.value === 1 ? styles.button : styles.buttonHidden }
                    onClick={this.props.handleChange1}
                >
                    Nagrywaj
                </Button>
                <Button
                    variant="outlined"
                    style={this.props.value === 2 ? styles.button : styles.buttonHidden}
                    onClick={this.props.handleChange2}
                >
                    Przegląd
                </Button>
                <Button
                    variant="outlined"
                    style={this.props.value === 3 ? styles.button : styles.buttonHidden}
                    onClick={this.props.handleChange3}
                    >
                    Statystyki
                </Button>
                <Button 
                    variant="outlined" 
                    style={this.props.value === 4 ? styles.button : styles.buttonHidden} 
                    onClick={this.props.handleChange4}
                    >
                    Trenuj
                </Button>
                <Button
                    variant="outlined"
                    style={this.props.value === 5 ? styles.button : styles.buttonHidden}
                    onClick={this.props.handleChange5}
                    >
                    Nagraj i Testuj
                </Button>
            </div>
        )
    }
}