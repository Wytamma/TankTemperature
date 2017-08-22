import React from 'react'
import PropTypes from 'prop-types'
import Tank from "./TankTwo"
import { Card } from 'semantic-ui-react'

class Home extends React.Component {
  constructor() {
    super();
    this.state = {
      probes: []
    }
  }


  render() {

    const probes = this.props.probes.map((probe, index) => {
      return(
          <Tank probe={probe} key={index}/>
      )
    })
    return (
      <Card.Group>
        {probes}
      </Card.Group>
    )
  }
}

Home.propTypes = {
  probes: PropTypes.arrayOf(
    PropTypes.shape({
      probe_ID: PropTypes.string.isRequired,
      name: function(props, propName, componentName) {
          const propValue = props[propName] // the actual value of `email` prop
          if (propValue === null) return
          if (typeof propValue === 'string') return
          return new Error(`${componentName} only accepts null or string`)
        }
    }).isRequired
  ).isRequired
}

export default Home;
