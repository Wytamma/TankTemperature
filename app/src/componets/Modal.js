import React from 'react'
import {Header, Modal } from 'semantic-ui-react'

class TankModal extends React.Component{
  constructor() {
    super();
  }
  render() {
    return (
  <Modal trigger={this.props.trigger} style={{height:"50%"}}>
    <Modal.Header>{this.props.probe.probe_ID}</Modal.Header>
    <Modal.Content>
      <p>Name: {this.props.probe.name}</p>
      <p>Max temperature alert: {this.props.probe.maxTemp}</p>
      <p>Min temperature alert: {this.props.probe.minTemp}</p>
    </Modal.Content>
  </Modal>
  )}
}

export default TankModal
