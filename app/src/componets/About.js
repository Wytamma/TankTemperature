import React from 'react'

class About extends React.Component {
  render() {
    return (
      <div>
        <p><b>An automated water temperature monitoring system.</b></p>
        <p>This system is built in three parts: This webapp,
          a RPi that records data, and the api server that deals the data.
        </p>
        <p>See the code on <a href="https://github.com/Wytamma/TankTemperature">Github</a></p>
      </div>
    )
  }
}

export default About;
