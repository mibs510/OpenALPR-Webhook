from blinker import Namespace
from apps.authentication.receiver import UserProfileReceiver


event_signals = Namespace()

tbls = UserProfileReceiver()

user_saved_signals = event_signals.signal('user-saved-signals')

user_saved_signals.connect(tbls.create_profile_by_user)

# delete user profile
delete_user_signals = event_signals.signal('delete-user-signals')
delete_user_signals.connect(tbls.delete_profile_by_user)
