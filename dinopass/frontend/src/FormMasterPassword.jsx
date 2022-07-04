import React from 'react'
import {Button, Form, Message} from 'semantic-ui-react'

import {useStoreActions, useStoreState} from 'easy-peasy';


const FormMasterPassword = () => {
  const {
    checkMasterPassword,
    createMasterPassword,
    setMasterPassword
  } = useStoreActions((actions) => actions);

  const {
    errorMessage,
    masterPassword,
    masterPasswordLoading
  } = useStoreState((state) => state)

  return (
    <>
      <Form loading={masterPasswordLoading}>
        <Form.Input
          required
          type='password'
          label='Master Password'
          placeholder='Your master password here'
          value={masterPassword}
          onChange={(e) => setMasterPassword(e.target.value)}
        />

        <Button
          disabled={!masterPassword}
          onClick={() => checkMasterPassword({master_password: masterPassword})}
        >
          Submit master password
        </Button>

        <Button
          disabled={!masterPassword}
          onClick={() => createMasterPassword({master_password: masterPassword})}
        >
          Create master password
        </Button>
      </Form>

      {errorMessage ?
        <Message error header='Error' content={errorMessage}/>
        :
        null
      }

    </>
  )

}

export default FormMasterPassword