import {Component} from "react";
import {Container} from 'semantic-ui-react';
import FormMasterPassword from "./FormMasterPassword";


class App extends Component {
  constructor(props) {
    super(props);

    this.state = {}
  }

  componentDidMount() {
  }

  render() {
    return (
      <div className="App">
        <Container style={{marginTop: '5%'}}>
          <FormMasterPassword/>
        </Container>
      </div>
    )
  }
}

export default App;
