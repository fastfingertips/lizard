import streamlit as st

class Input:
    textbox_placeholder = 'Enter a list **url** or **username/list-title**.'

    def __init__(self):
        pass

    def process_data(self):
        query_data = st.query_params.to_dict()

        input_data = st.text_input(
            value=query_data['q'] if 'q' in query_data else '',
            label=self.textbox_placeholder
            )

        if 'q' in query_data:
            input_type = 'query'
        else:
            input_type = 'input' if input_data else None

        st.query_params.clear()

        data = {
            'user_input_data': input_data,
            'user_input_type': input_type
        }

        return data if data else None

    @staticmethod
    def convert_to_url(data):
        """
        normal:
            fastfingertips/list_name                              -> fastfingertips/list_name
            fastfingertips/list/list_name                         -> fastfingertips/list_name
            fastfingertips/list/list_name/detail                  -> fastfingertips/list_name

        specific names('list' or 'detail'):
            # if a list's name is 'list'?
            `fastfingertips/list`                                 -> fastfingertips/list
            `fastfingertips/list/list`                            -> fastfingertips/list
            `fastfingertips/list/list/detail`                     -> fastfingertips/list

            # if a list's name is 'detail'?
            `fastfingertips/detail`                               -> fastfingertips/detail
            `fastfingertips/detail/detail`                        -> fastfingertips/detail
            `fastfingertips/list/detail`                          -> fastfingertips/detail
            `fastfingertips/list/detail/detail`                   -> fastfingertips/detail

        filters:
            `fastfingertips/list_name/decade/1990s/genre/crime+-comedy/by/popular`
            `fastfingertips/list/list_name/decade/1990s/genre/crime+-comedy/by/popular`
            `fastfingertips/list/list_name/detail/decade/1990s/genre/crime+-comedy/by/popular`

        extras: 
            checks the / sign at the end and beginning of the data.
        """
        if '/' in data:

            # 1. remove '/' from start and end of string
            if len(data) <= 2:
                print('Error: Data is too short.')
                return None

            if data[0] == '/': data = data[1:]
            if data[-1] == '/': data = data[:-1]
                
            # 2. split data by '/'
            if '/' not in data:
                print('Error: Data does not contain a / character.')
                return None

            data_blocks = data.split('/')
            username = data_blocks[0]
            data_blocks = data_blocks[1:] 

            if len(data_blocks) == 1:
                list_slug = data_blocks[0]
                data_blocks.clear()
            else:
                if data_blocks[0] == 'list':

                    if data_blocks[1] == 'list':
                        list_slug = data_blocks[1]
                        data_blocks = data_blocks[2:]
                        if data_blocks:
                            if data_blocks[0] == 'detail':
                                # /list/list/detail
                                data_blocks = data_blocks[1:]

                    elif data_blocks[1] == 'detail':
                        list_slug = data_blocks[1]
                        data_blocks = data_blocks[2:]
                        if data_blocks:
                            if data_blocks[0] == 'detail':
                                # /list/detail/detail
                                data_blocks = data_blocks[1:]

                    else:
                        # list/list_name
                        list_slug = data_blocks[1]
                        data_blocks = data_blocks[2:]
                        if data_blocks:
                            # list/list_name/?
                            if data_blocks[0] == 'detail':
                                # list/list_name/detail
                                data_blocks = data_blocks[1:]

                elif data_blocks[0] == 'detail':
                    if data_blocks[1] == 'detail':
                        list_slug = data_blocks[0]
                        data_blocks = data_blocks[2:]
                    else:
                        list_slug = data_blocks[0]
                        data_blocks = data_blocks[1:]
                        pass
                else:
                    list_slug = data_blocks[0]
                    data_blocks = data_blocks[1:]
                    pass

            print(f'List name: {list_slug}')
            print(f'Username: {username}')
            print(f'Blocks: {data_blocks}')

            try:
                if all([username, list_slug]):
                    filters = ''
                    if data_blocks:
                        filters = '/'.join(data_blocks)
                    return f'https://letterboxd.com/{username}/list/{list_slug}/' + filters
                else:
                    print('Error: Username or list title is empty.')
            except Exception as e:
                print(f'Error: {e}')
                pass
        else:
            # FUTURE: operations entered with only username or list name
            print('Error: Data does not contain a / character.')

        return None
