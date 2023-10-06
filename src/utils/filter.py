def remove_password_from_users(users):
    user_dicts = []
    for user in users:
        user_dict = user.__dict__
        user_dict.pop('_sa_instance_state', None)
        user_dict.pop('password', None)
        user_dicts.append(user_dict)
    return user_dicts