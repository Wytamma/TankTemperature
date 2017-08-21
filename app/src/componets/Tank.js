import React from 'react'
import PropTypes from 'prop-types'
import { Col, Row } from 'react-bootstrap';
import _Urls from '../_Urls'
import { Sparklines, SparklinesLine } from 'react-sparklines';
import ReactFitText from 'react-fittext'
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

const round = (value, precision) => {
    var multiplier = Math.pow(10, precision || 0);
    return Math.round(value * multiplier) / multiplier;
}

const setColor = (temps, maxVal, minVal) => {
  let color = 'green';
  let min = Math.min.apply(null, temps);
  let max = Math.max.apply(null, temps);
    if (min < minVal || max > maxVal) {
      color = 'orange'
    }
    if (temps[-1] < minVal || temps[-1] > maxVal) { //the most recnent value
      color = 'red'
    }
  return color
}

class Tank extends React.Component {
  constructor() {
    super();
    this.state = {
      temp:"",
      temps:[]
    }
  }

  componentWillMount() {
    console.log("Getting data...");
    this.getData(100)

  }
  componentDidMount() {
    setInterval(() => {
      console.log("Updating data...");
      if (this.refs.myRef) {
        this.getData(100)
      }
    }, (1000*60*10));
  }
  render() {

    return (

      <Col sm={12} md={12} lg={6}>
      <div style={styles.card} ref="myRef">
        <div style={styles.HeaderContainer}>
        <Header title={this.props.probe.name ? this.props.probe.name:this.props.probe.probe_ID}/>
        </div>
        <div style={styles.container}>
        <Row>
          <Col xs={10} style={styles.spark}>
          <Sparklines data={this.state.temps}>
              <SparklinesLine color={this.state.color} style={{ strokeWidth: 2}} />
          </Sparklines>
          </Col>
          <Col xs={2} style={styles.temp}>
          <ReactFitText compressor={.35}>
            <h1 style={styles.tempText}>{this.state.temp}</h1>
          </ReactFitText>
          </Col>
        </Row>
        </div>
      </div>
      </Col>

    )
  }
  getData = (limit) => {
    fetch(_Urls.APIBASEURL + "/temps/" + this.props.probe.probe_ID + "?limit="+limit)
    .then(results => {
      return results.json();
    }).then(data => {
      const reducedData = data.data.map(item => { return item.temperature }).reverse();
      (data.data.length > 0) ?
      this.setState({
        temp: round(data.data[0].temperature, 2)+"˚C",
        temps: reducedData,
        color: setColor(reducedData, 28, 20)
      }):
      this.setState({temp: "No data"});
    })
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
