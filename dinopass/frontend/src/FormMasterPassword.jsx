import React from 'react'
import {Button, Form, Message} from 'semantic-ui-react'

import {useStoreActions, useStoreState} from 'easy-peasy';


const FormMasterPassword = () => {
  const {
    check,
    create,
    setValue
  } = useStoreActions((actions) => actions.dinopassModels.masterPassword);

  const {
    error,
    value,
    loading
  } = useStoreState((state) => state.dinopassModels.masterPassword)

  return (
    <>
      <Form loading={loading}>
        <Form.Input
          required
          type='password'
          label='Master Password'
          placeholder='Your master password here'
          value={value}
          onChange={(e) => setValue(e.target.value)}
        />

        <Button
          disabled={!value}
          onClick={() => check({master_password: value})}
        >
          Submit master password
        </Button>

        <Button
          disabled={!value}
          onClick={() => create({master_password: value})}
        >
          Create master password
        </Button>
      </Form>

      {error ?
        <Message error header='Error' content={error}/>
        :
        null
      }

    </>
  )

}

export default FormMasterPassword