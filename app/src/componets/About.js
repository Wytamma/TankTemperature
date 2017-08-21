import React from 'react'

class About extends React.Component {
  render() {
    return (
      <div>
        <h2>An automated water temperature monitoring system.</h2>
        <p>This system is built in three parts:</p>
          <ul>
            <li><p>A <a href="https://www.raspberrypi.org/">Raspberry pi</a> that records data from temperature sensors</p></li>
            <li><p>This webapp, built with <a href="https://facebook.github.io/react/">React.js</a> for viewing data</p></li>
            <li><p>A <a href="http://flask.pocoo.org/">Flask</a> API backed by <a href="https://www.mongodb.com/">MongoDB</a> that saves and sends the data</p></li>
          </ul>
        <br></br><p>See the code on <a href="https://github.com/Wytamma/TankTemperature">Github</a> or contact Wytamma: <a href="mailto:name@email.com">wytamma.wirth@me.com</a></p>
      </div>
    )
  }
}

export default About;
