from flask import Blueprint
from flask_restful import Api
from api.events import EventDetail, UserEvents, AllEvents, EventEditor, EventCreate
from api.notifications import UserNotifications, UserInvitationNotifications, UserGeneralNotifications, MarkNotificationAsRead
from api.groups import GroupCreate, GroupJoin, GroupLeave, GroupDelete, GroupEdit, GroupInvite, UserGroups, GroupDetail
from api.auth import UserRegister, UserLogin, UserLogout, CheckAuth
from api.user import UserProfile, ChangePassword, DeleteAccount, UserSearch
from api.admin import AdminUserList, AdminUserActions, DeleteAccount
from api.friends import FriendRequest, FriendResponse, FriendList, FriendDetail, RemoveFriend
from api.events_drafts import EventDraftCreate, VoteForDraft, FinalizeDraft

api_bp = Blueprint('api', __name__)
api = Api(api_bp)

api.add_resource(UserEvents, '/events/my')
api.add_resource(EventDetail, '/events/<int:event_id>')
api.add_resource(AllEvents, '/events/all')
api.add_resource(EventEditor, '/events/<int:event_id>/edit')
api.add_resource(EventCreate, '/events/create')

api.add_resource(UserNotifications, '/notifications')
api.add_resource(UserInvitationNotifications, '/notifications/invitations')
api.add_resource(UserGeneralNotifications, '/notifications/general')
api.add_resource(MarkNotificationAsRead, '/notifications/<int:notification_id>/mark-read')

api.add_resource(GroupCreate, '/groups')
api.add_resource(GroupJoin, '/groups/<int:group_id>/join')
api.add_resource(GroupLeave, '/groups/<int:group_id>/leave')
api.add_resource(GroupDelete, '/groups/<int:group_id>')
api.add_resource(GroupEdit, '/groups/<int:group_id>')
api.add_resource(GroupInvite, '/groups/<int:group_id>/invite')
api.add_resource(UserGroups, '/groups/my')
api.add_resource(GroupDetail, '/groups/<int:group_id>')

api.add_resource(UserRegister, '/auth/register')
api.add_resource(UserLogin, '/auth/login')
api.add_resource(UserLogout, '/auth/logout')
api.add_resource(CheckAuth, '/auth/check')

api.add_resource(UserProfile, '/user/profile')
api.add_resource(ChangePassword, '/user/change-password')
api.add_resource(DeleteAccount, '/user/delete')
api.add_resource(UserSearch, '/user/search')

api.add_resource(AdminUserList, '/admin/users')
api.add_resource(AdminUserActions, '/admin/users/<int:user_id>')

api.add_resource(FriendRequest, '/friends/request')
api.add_resource(FriendResponse, '/friends/request/<int:request_id>')
api.add_resource(FriendList, '/friends')
api.add_resource(FriendDetail, '/friends/<int:friend_id>')
api.add_resource(RemoveFriend, '/friends/<int:friend_id>/remove')

api.add_resource(EventDraftCreate, '/events_drafts/create')
api.add_resource(VoteForDraft, '/events_drafts/vote/<int:event_draft_id>')
api.add_resource(FinalizeDraft, '/events_drafts/finale/<int:event_draft_id>')