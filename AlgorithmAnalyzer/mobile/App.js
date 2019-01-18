import React, {Component} from 'react';
import { 
          StyleSheet, 
          ImageBackground,
          Image,
          Text,
          View,
          TouchableHighlight 
        } from 'react-native';
import { 
          Card, 
          Item, 
          Input,
          ListItem,
          CheckBox,
          Button,
          Icon
} from 'native-base'
import { Buffer } from 'buffer'
import Permissions from 'react-native-permissions'
import Sound from 'react-native-sound'
import AudioRecord from 'react-native-audio-record'
import {create} from 'apisauce'
import api_config from './api_config.json'
import Toast, {DURATION} from 'react-native-easy-toast'
import RNFetchBlob from 'rn-fetch-blob'
import RNFS from 'react-native-fs'

export default class App extends Component {
  state={
    audioFile: '',
    recording: false,
    loaded: false,
    paused: true,
    type: 'test',
    username: '',
    audio: '',
    sound: ''
  }
  pressCheckbox(type){
    this.setState({
      type: type
    })
  }
  async componentDidMount() {
    await this.checkPermission();

    const options = {
      sampleRate: 16000,
      channels: 1,
      bitsPerSample: 16,
      wavFile: 'test.wav'
    };

    AudioRecord.init(options);

    AudioRecord.on('data', data => {
      const chunk = Buffer.from(data, 'base64');
      this.setState({
        audio: data
      })
    });
  }

  checkPermission = async () => {
    const p = await Permissions.check('microphone');
    console.log('permission check', p);
    if (p === 'authorized') return;
    this.requestPermission();
  };

  requestPermission = async () => {
    const p = await Permissions.request('microphone');
    console.log('permission request', p);
  };

  start = () => {
    console.log('start record');
    this.setState({ audioFile: '', recording: true, loaded: false });
    AudioRecord.start();
  };

  stop = async () => {
    if (!this.state.recording) return;
    console.log('stop record');
    let audioFile = await AudioRecord.stop();
    console.log('audioFile', audioFile);
    this.setState({ audioFile, recording: false });
  };

  load = () => {
    return new Promise((resolve, reject) => {
      if (!this.state.audioFile) {
        return reject('file path is empty');
      }

      this.sound = new Sound(this.state.audioFile, '', error => {
        if (error) {
          console.log('failed to load the file', error);
          return reject(error);
        }
        this.setState({ loaded: true });
        return resolve();
      });
    });
  };

  play = async () => {
    if (!this.state.loaded) {
      try {
        await this.load();
      } catch (error) {
        console.log(error);
      }
    }

    this.setState({ paused: false });
    Sound.setCategory('Playback');
    console.log('lul', this.sound)
    this.sound.play(success => {
      if (success) {
        console.log('successfully finished playing');
      } else {
        console.log('playback failed due to audio decoding errors');
      }
      this.setState({ paused: true });
      // this.sound.release();
    });
  };

  pause = () => {
    this.sound.pause();
    this.setState({ paused: true });
  };


  addSound(){
    const file = {
      uri: 'file:///data/user/0/com.glosbioandroid/files/test.wav',
      name: 'test.wav',
      type: 'audio/wav'
    }
    let fd = new FormData()
    fd.append('file', file)
    fd.append('username', 'dupa')
    fetch(api_config.usePath+`/audio/${this.state.type}`, {
      method: 'POST',
      body: fd })
/*
    fd.append("username", this.state.username);
    fd.append("file", this.state.audio )
    fetch('POST', api_config.usePath+`/audio/${this.state.type}`, {
    Authorization : api_config.apiKey,
    'Content-Type' : 'multipart/form-data',
    },fd/* [
    // append field data from file path
    {
      username : this.state.username,
      // Change BASE64 encoded data to a file path with prefix `RNFetchBlob-file://`.
      // Or simply wrap the file path with RNFetchBlob.wrap().
      data: RNFetchBlob.wrap(RNFetchBlob.fs.asset(RNFS.DocumentDirectoryPath +'/test.wav'))
    }/*,
    {
      name : 'ringtone',
      filename : 'ring.mp3',
      // use custom MIME type
      type : 'application/mp3',
      // upload a file from asset is also possible in version >= 0.6.2
      data : RNFetchBlob.wrap(RNFetchBlob.fs.asset('default-ringtone.mp3'))
    }
    // elements without property `filename` will be sent as plain text
    { name : 'name', data : 'user'},
    { name : 'info', data : JSON.stringify({
      mail : 'example@example.com',
      tel : '12345678'
    })},*/
  .then((resp) => {
    console.log('zajebiście', resp)
  }).catch((err) => {
    console.log('chujowo', err)
  })
  }
  /*addSound(){
    var self = this
    var lol = 'xd'
    RNFS.readDir(RNFS.DocumentDirectoryPath) // On Android, use "RNFS.DocumentDirectoryPath" (MainBundlePath is not defined)
      .then((result) => {
        console.log('GOT RESULT', result[0]);
        // stat the first file
        let fd = new FormData();
			fd.append("username", this.state.username);
      fd.append("file", result[0] )
            console.log('fd', fd)
            const api = create({
                baseURL: api_config.usePath,
                headers: {
                  "Content-Type": "multipart/form-data",
                  "Authorization": api_config.apiKey
              }
            })
            api
                  .post(`/audio/${this.state.type}`, fd)
                  .then((response) => {
                      console.log('zajebiście', response)
                    }) 
                  .catch((error)=>{
                    console.log('chujowo', error)
                  })
        return Promise.all([RNFS.stat(result[0].path), result[0].path]);
      })
      .then((statResult) => {
        if (statResult[0].isFile()) {
          // if we have a file, read it
          return RNFS.readFile(statResult[1], 'utf8');
        }

        return 'no file';
      })
      .then((contents) => {
        // log the file contents
        console.log(contents);
      })
      .catch((err) => {
        console.log(err.message, err.code);
      });
  }*/

  render() {
    const { recording, paused, audioFile } = this.state;
    return (
      <ImageBackground
        source={require('./img/background.jpg')}
        style={styles.bgimage}
        resizeMode='cover'
      >
        <Image 
          source={require('./img/logo.png')}
          style={styles.logo}
          />
          <Card style={styles.mainCard}>
            <Card style={styles.inputCard}>
              <Item style={styles.inputItem}>
                <Input 
                  placeholder="Username" 
                  style={{color: 'white'}} 
                  onChangeText={(username) => this.setState({username})}
                  />
              </Item> 
            </Card>
            <Text style={{color: 'white', margin: 20}}>Wybierz typ nagrania:</Text>
            <ListItem style={{width: '100%', alignItems: 'center'}}>
              <CheckBox 
                checked={this.state.type === 'train'} 
                color='red'
                onPress={()=>this.pressCheckbox('train')}
              />
                <Text style={{color: 'white', marginLeft: 10, marginRight: 10 }}>Trenowanie</Text>
              <CheckBox 
                checked={this.state.type === 'test'} 
                color='red'
                onPress={()=>this.pressCheckbox('test')}
              />
                <Text style={{color: 'white', marginLeft: 10, marginRight: 10}}>Test</Text>
            </ListItem>
            <View style={{marginTop: 10}}>
              <Button light style={{margin: 5}} iconRight onPress={()=>this.addSound()} >
                <Text style={{padding: 5, marginLeft: 10}}>Save</Text><Icon name='cloud-upload' />
              </Button>
            </View>
          </Card>
          <Card style={styles.mainCard}>
          <TouchableHighlight 
              style={ !recording ? styles.circleButtonRed : styles.circleButtonWhite } 
              onPress={ !recording ? this.start : this.stop }
              >
              <View style={ !recording ? styles.circleButtonRecord : styles.squareButtonRecord}/>
          </TouchableHighlight>
          <View style={{
            marginTop: 10, 
            flexDirection: 'row', 
            justifyContent: 'space-around',
            width: '100%'
            }}>
            <Button 
              success 
              iconRight  
              onPress={this.play} 
              style={{width: 150, justifyContent: 'center'}}
              disabled={!audioFile}
              >
              <Icon name='play' /><Text>Play</Text>
            </Button>
            <Button 
              warning 
              iconRight  
              onPress={this.pause} 
              style={{width: 150, justifyContent: 'center'}}
              disabled={!audioFile}
              >
              <Icon name='pause' /><Text>Pause</Text>
            </Button>
          </View>
          </Card>
          <Toast
                    ref="toasterr"
                    style={{backgroundColor:'red'}}
                    position='top'
                    positionValue={200}
                    fadeInDuration={750}
                    fadeOutDuration={1000}
                    opacity={0.8}
                    textStyle={{color:'black'}}
                />
      </ImageBackground>
    );
  }
}

const styles = StyleSheet.create({
  bgimage: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center'
  },
  logo: {
    width: 100,
    height: 100
  },
  mainCard: {
    width: '90%',
    backgroundColor: 'rgba(0,0,0, 0.5)', 
    alignItems: 'center',
    justifyContent: 'center',
    borderColor: 'red', 
    padding: 15
  },
  inputCard: {
    width: '50%', 
    backgroundColor: 'rgba(0,0,0, 0.5)', 
    alignItems: 'center'
  },
  inputItem: {
    width: '90%', 
    borderWidth: 3, 
    borderColor: 'white', 
    margin: 3
  },
  circleButtonRed: {
    width: 60,
    height: 60,
    borderRadius: 100,
    backgroundColor: 'red',
    justifyContent: 'center',
    alignItems: 'center'
  },
  circleButtonWhite: {
    width: 60,
    height: 60,
    borderRadius: 100,
    backgroundColor: 'white',
    justifyContent: 'center',
    alignItems: 'center'
  },
  circleButtonRecord: {
    width: 15,
    height: 15,
    borderRadius: 100,
    backgroundColor: 'white'
  },
  squareButtonRecord: {
    width: 15,
    height: 15,
    backgroundColor: 'black'
  }
});
