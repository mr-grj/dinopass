from credential import Credential
from models import SESSION
from helpers import command_line_parser, pp


def main():
    args = command_line_parser().parse_args()

    session = SESSION()

    if args.all:
        data = Credential(session).get_all()
        if not data:
            print('There are no credentials stored yet!')
        pp(title='ALL CREDENTIALS', data=data)

    elif args.purge:
        Credential(session).purge()

    elif args.create:
        name, group, password = args.create
        Credential(session).create(name, group, password)

    elif args.get:
        field, value = args.get
        data = Credential(session).get(field, value)
        if not data:
            print(f'There is no record with {field}={value}!')
            return
        pp(title=f'CREDENTIAL for {value}', data=data)

    elif args.update:
        field, value, field_to_update, new_value = args.update
        Credential(session).update(field, value, field_to_update, new_value)

    elif args.delete:
        field, value = args.delete
        Credential(session).delete(field, value)

    else:
        raise ValueError('Invalid option')


if __name__ == '__main__':
    main()
