import React from 'react'
import PropTypes from 'prop-types'
import _Urls from '../_Urls'
import { Sparklines, SparklinesLine } from 'react-sparklines';
import { Card, Icon, Popup } from 'semantic-ui-react'
import 'semantic-ui-css/semantic.min.css';
import Toggle from 'react-toggle'
import TankModal from './Modal'

const mql = window.matchMedia(`(min-width: 850px)`);

const round = (value, precision) => {
    var multiplier = Math.pow(10, precision || 0);
    return Math.round(value * multiplier) / multiplier;
}

const setColor = (temps, max, min, maxVal, minVal) => {
  let color = 'green';
  if (min < minVal ) {
      color = 'orange'
  } else if (max > maxVal) {
      color = 'orange'
  }
  if (temps[temps.length - 1] < minVal || temps[temps.length - 1] > maxVal) { //the most recnent value
      color = 'red'
  }
  return color
}

class Tank extends React.Component {
  constructor() {
    super();
    this.state = {
      mql: mql,
      fluid: false,
      temp:"",
      temps:[],
      snooze: false,
    };
    this.mediaQueryChanged = this.mediaQueryChanged.bind(this);

  }

  componentWillMount() {
    mql.addListener(this.mediaQueryChanged);
    this.setState({mql: mql, fluid: mql.matches, alertSnooze: this.props.probe.alertSnooze});
    console.log("Getting data...");
    this.getData(100, this.props.probe.maxTemp, this.props.probe.minTemp)
  }
  componentWillUnmount() {
    this.state.mql.removeListener(this.mediaQueryChanged);
  }

  componentDidMount() {
    setInterval(() => {
      if (this.refs.myRef) {
        console.log("Updating data...");
        this.getData(100, this.props.probe.maxTemp, this.props.probe.minTemp)
      }
    }, (1000*60*10));
  }
  render() {

    return (
      <Card fluid={!this.state.fluid} ref="myRef">
        <div style={{position: "absolute", paddingLeft:"90%", paddingTop:"1%"}}>
        <TankModal
          trigger={<a style={{padding: 10}}><Icon name='info circle'/></a>}
          probe={this.props.probe}
        />
        </div>
        { (new Date().getTime() - this.state.lastRecodTime) > (1000*60*20) ? <Popup trigger={<Icon style={{position: "absolute"}} name='warning circle' color="red"/>}>
          Connection error!<br/>Data is not current.<br/>{round(((((new Date().getTime() - this.state.lastRecodTime)/1000)/60)/60), 2)} hours old.
        </Popup>:""}

        <Sparklines data={this.state.temps} height={80}>
            <SparklinesLine color={this.state.color} style={{ strokeWidth: 2}} />
        </Sparklines>
        <Card.Content>
          <Card.Header style={{fontSize:32, marginBottom:0}}>
            {this.state.temp}
          </Card.Header>
          <Card.Meta>
            <span style={{fontSize:12}} className='date'>
              {this.state.hours ? "Past " + this.state.hours + " hours: " + this.state.min + " - " + this.state.max + "˚C":""}
            </span>
          </Card.Meta>
          <Card.Description style={{fontSize:18}}>
            {this.props.probe.name ? this.props.probe.name:this.props.probe.probe_ID}
          </Card.Description>
        </Card.Content>
        <Card.Content extra style={{textAlign:'right'}}>
          <label >
            <span>Snooze alerts  </span>
            <Toggle
              defaultChecked={(this.state.alertSnooze <= new Date().getTime()) ? false : true}
              onChange={this.handleSnoozeChange}
              style={{marginBottom:0}}/>
          </label>
        </Card.Content>
      </Card>

    )
  }
  getData = (limit, maxVal, minVal) => {
    fetch(_Urls.APIBASEURL + "/temps/" + this.props.probe.probe_ID + "?limit="+limit)
    .then(results => {
      return results.json();
    }).then(data => {
      const reducedData = data.data.map(item => { return item.temperature }).reverse();
      const min = Math.min.apply(null, reducedData);
      const max = Math.max.apply(null, reducedData);
      (data.data.length > 0) ?
      this.setState({
        temp: round(reducedData[reducedData.length - 1], 2)+"˚C",
        temps: reducedData,
        color: setColor(reducedData, max, min, maxVal, minVal),
        max: round(max, 1),
        min: round(min, 1),
        hours: round(((((data.data[0].time - data.data[data.data.length - 1].time)/1000)/60)/60), 1),
        lastRecodTime: data.data[0].time,
      }):
      this.setState({temp: "No data"});
      //
    })
  }

  mediaQueryChanged() {
    this.setState({
      mql: mql,
      fluid: this.state.mql.matches,
    });
  }

  handleSnoozeChange = (event) => {
    if (event.target.checked) {
      // snooze
      let hours = 7
      let alertSnooze = (new Date().getTime() + (1000 * 60 * 60 * hours));
      this.updateAlertSnooze(alertSnooze)
    } else {
      // reset snooze
      this.updateAlertSnooze(new Date().getTime())
    }

  }

  updateAlertSnooze = (newAlertSnooze) => {
    let data = this.props.probe
    data.alertSnooze = newAlertSnooze
    fetch(_Urls.APIBASEURL + "/probes", {
            method: 'PUT',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(data),
        })
        .then(function(response) {
        if (!response.ok) {
            console.log("not ok");
            console.log(response.json().message);
            throw Error(response.statusText);
        }
        return response;
        })
        .then(reponse => {
          this.setState({
            alertSnooze: newAlertSnooze
          });
        }).catch(err => {
            console.log('request failed', err);
        });
  }

}



Tank.propTypes = {
  probe: PropTypes.shape({
    probe_ID: PropTypes.string.isRequired,
    name: function(props, propName, componentName) {
        const propValue = props[propName] // the actual value of `email` prop
        if (propValue === null) return
        if (typeof propValue === 'string') return
        return new Error(`${componentName} only accepts null or string`)
      }
  }).isRequired
}

export default Tank;
