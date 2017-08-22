import React from 'react'
import PropTypes from 'prop-types'
import _Urls from '../_Urls'
import { Sparklines, SparklinesLine } from 'react-sparklines';
import { Card, Icon } from 'semantic-ui-react'
import 'semantic-ui-css/semantic.min.css';
import Toggle from 'react-toggle'

const styles = {
  card: {
    borderRadius: 5,
    borderStyle: "solid",
    borderColor: "#2c3e50",
    borderWidth: 1,
    marginBottom: 20,
    backgroundColor: "#ecf0f1",
  },
  HeaderContainer: {
    backgroundColor: "#2c3e50",
    textAlign: "center",
  },
  HeaderText: {
    color: "#27ae60",
    fontSize: 32,
    padding: 5,
  },
  container: {
    //padding: 5,
  },
  temp: {
    width: "25%",
    textAlign: "left",
    padding: 0,
  },
  tempText: {
  },
  spark: {
    width: "75%",
  }
};

const mql = window.matchMedia(`(min-width: 850px)`);

const round = (value, precision) => {
    var multiplier = Math.pow(10, precision || 0);
    return Math.round(value * multiplier) / multiplier;
}

const setColor = (temps, maxVal, minVal) => {
  let color = 'green';
  let min = Math.min.apply(null, temps);
  let max = Math.max.apply(null, temps);
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
      snooze: false
    };
    this.mediaQueryChanged = this.mediaQueryChanged.bind(this);

  }

  componentWillMount() {
    mql.addListener(this.mediaQueryChanged);
    this.setState({mql: mql, fluid: mql.matches});
    console.log("Getting data...");
    this.getData(100, this.props.probe.maxTemp, this.props.probe.minTemp)

  }
  componentWillUnmount() {
    this.state.mql.removeListener(this.mediaQueryChanged);
  }
  mediaQueryChanged() {
    this.setState({
      mql: mql,
      fluid: this.state.mql.matches,
    });
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
      <Card fluid={!this.state.fluid}>
        <div style={{position: "absolute", paddingLeft:"90%", paddingTop:"1%"}}>
          <a style={{padding: 10}}>
          <Icon size={20} name='info circle' />
          </a>
        </div>
        <Sparklines data={this.state.temps} height={80}>
            <SparklinesLine color={this.state.color} style={{ strokeWidth: 2}} />
        </Sparklines>
        <Card.Content>
          <Card.Header style={{fontSize:32, marginBottom:0}}>
            {this.state.temp}
          </Card.Header>
          <Card.Meta>
            <span style={{fontSize:12}} className='date'>
              10:11:13 23/8/17
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
              defaultChecked={this.state.snooze}
              onChange={this.handleSnoozeChange}
              style={{marginBottom:0}}/>
          </label>
        </Card.Content>
      </Card>

    )
  }
  getData = (limit, maxTemp, minTemp) => {
    fetch(_Urls.APIBASEURL + "/temps/" + this.props.probe.probe_ID + "?limit="+limit)
    .then(results => {
      return results.json();
    }).then(data => {
      const reducedData = data.data.map(item => { return item.temperature }).reverse();
      (data.data.length > 0) ?
      this.setState({
        temp: round(reducedData[reducedData.length - 1], 2)+"˚C",
        temps: reducedData,
        color: setColor(reducedData, maxTemp, minTemp)
      }):
      this.setState({temp: "No data"});
    })
  }
  mediaQueryChanged() {
    this.setState({
      mql: mql,
      fluid: this.state.mql.matches,
    });
  }
  handleSnoozeChange() {
    console.log("snooze");
  }
}

const Header = ({ title }) => {
  return (
      <p style={styles.HeaderText}>
        {title}
      </p>
  );
};



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
