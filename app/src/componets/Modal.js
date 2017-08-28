import React from 'react'
import { Modal, Icon } from 'semantic-ui-react'

class TankModal extends React.Component{
  state = { open: false }
  close = () => this.setState({ open: false })

  render() {
    return (
  <Modal
    trigger={this.props.trigger}
    closeIcon={<div style={{textAlign:'right'}}><Icon style={{margin:0, padding:0}} name='close' size='large'/></div>}
    style={{height:"50%"}}>
    <Modal.Header>{this.props.probe.probe_ID}</Modal.Header>
    <Modal.Content>
    <div>
      <p>Name: {this.props.probe.name}</p>
      <p>Max temperature alert: {this.props.probe.maxTemp}</p>
      <p>Min temperature alert: {this.props.probe.minTemp}</p>
    </div>
    </Modal.Content>
  </Modal>
  )}
}

export default TankModal
