import {action} from "easy-peasy";

const menu = {
  open: true,
  setOpen: action(state => {
    state.open = !state.open
  })
}

export default menu;