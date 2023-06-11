from .models import UserProfile, User


class UserProfileReceiver:
    def create_profile_by_user(self, context):
        """ Create profile  """
        # profile = UserProfile.query.filter_by(user=context['user_id']).first()
        profile = UserProfile.find_by_user_id(context['user_id'])
        if profile is None:
            create_profile = UserProfile()
            if context['email'] is None:
                create_profile.user = context['user_id']
                create_profile.save()

            create_profile.user = context['user_id']
            create_profile.email = context['email']
            create_profile.save()
        return True
    
    def delete_profile_by_user(self, context):
        """ delete profile  """
        profile = UserProfile.find_by_user_id(context['user_id'])
        if profile is not None:
            profile.delete_from_db()
        return True

