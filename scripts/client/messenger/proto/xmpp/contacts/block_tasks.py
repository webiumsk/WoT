# Embedded file name: scripts/client/messenger/proto/xmpp/contacts/block_tasks.py
from gui.shared.utils import findFirst
from messenger.m_constants import USER_ACTION_ID, USER_TAG, PROTO_TYPE, CLIENT_ACTION_ID
from messenger.proto.xmpp import entities, errors
from messenger.proto.xmpp.contacts.tasks import TASK_RESULT, ContactTask, SeqTask
from messenger.proto.xmpp.extensions import blocking_cmd
from messenger.proto.xmpp.find_criteria import ItemsFindCriteria
from messenger.proto.xmpp.log_output import g_logOutput, CLIENT_LOG_AREA
from messenger.proto.xmpp.xmpp_constants import XMPP_ITEM_TYPE
from messenger.proto.xmpp.xmpp_items import BlockItem

def _syncBlockItem(storage, jid, name = '', dbID = 0):
    dbID = jid.getDatabaseID()
    user = storage.getUser(dbID, PROTO_TYPE.XMPP)
    if user:
        if user.isCurrentPlayer():
            return None
        if user.getItemType() == XMPP_ITEM_TYPE.BLOCKING_LIST:
            user.update(name=name, trusted=True)
        else:
            user.update(name=name, item=BlockItem(jid))
        user.addTags({USER_TAG.MUTED})
    else:
        user = entities.XMPPUserEntity(dbID, name=name, item=BlockItem(jid), tags={USER_TAG.MUTED})
        storage.setUser(user)
    return user


class _BlockItemTask(ContactTask):

    def sync(self, name, groups, to, from_):
        return self._result


class BlockListResultTask(SeqTask):

    def result(self, pyGlooxTag):
        handler = blocking_cmd.BlockListHandler()
        storage = self.usersStorage
        for jid, info in handler.handleTag(pyGlooxTag):
            _syncBlockItem(storage, jid, **info)

        self.usersStorage.removeTags({USER_TAG.CACHED}, ItemsFindCriteria(XMPP_ITEM_TYPE.BLOCKING_LIST))
        self._result = TASK_RESULT.REMOVE

    def _doRun(self, client):
        self._iqID = client.sendIQ(blocking_cmd.BlockListQuery())


class AddBlockItemTask(_BlockItemTask):

    def set(self, pyGlooxTag):
        result = blocking_cmd.BlockItemHandler().handleTag(pyGlooxTag)
        jid, _ = findFirst(None, result, ('', {}))
        if jid != self._jid:
            return
        else:
            user = _syncBlockItem(self.usersStorage, self._jid, name=self._name)
            if user:
                g_logOutput.debug(CLIENT_LOG_AREA.BLOCK_LIST, 'Block item is added', user)
                self._doNotify(USER_ACTION_ID.IGNORED_ADDED, user)
                self._doNotify(USER_ACTION_ID.MUTE_SET, user, False)
            self._result = TASK_RESULT.REMOVE
            return

    def _doRun(self, client):
        self._iqID = client.sendIQ(blocking_cmd.BlockItemQuery(self._jid))

    def _getError(self, pyGlooxTag):
        return errors.createServerActionError(CLIENT_ACTION_ID.ADD_IGNORED, pyGlooxTag)


class RemoveBlockItemTask(_BlockItemTask):

    def set(self, pyGlooxTag):
        result = blocking_cmd.UnblockItemHandler().handleTag(pyGlooxTag)
        jid, _ = findFirst(None, result, ('', {}))
        if jid != self._jid:
            return
        else:
            user = self._getUser()
            if user and user.getItemType() in XMPP_ITEM_TYPE.BLOCKING_LIST:
                user.update(item=None)
                user.removeTags({USER_TAG.MUTED})
                g_logOutput.debug(CLIENT_LOG_AREA.BLOCK_LIST, 'Block item is removed', user)
                self._doNotify(USER_ACTION_ID.IGNORED_REMOVED, user)
                self._doNotify(USER_ACTION_ID.MUTE_UNSET, user, False)
                if user.isFriend():
                    self._doNotify(USER_ACTION_ID.FRIEND_ADDED, user, False)
            self._result = TASK_RESULT.REMOVE
            return

    def _doRun(self, client):
        self._iqID = client.sendIQ(blocking_cmd.UnblockItemQuery(self._jid))

    def _getError(self, pyGlooxTag):
        return errors.createServerActionError(CLIENT_ACTION_ID.REMOVE_IGNORED, pyGlooxTag)
