# Embedded file name: scripts/client/messenger/proto/xmpp/entities.py
from collections import deque
from messenger.m_constants import PROTO_TYPE, USER_TAG, MESSAGES_HISTORY_MAX_LEN
from messenger.proto.entities import UserEntity, ChannelEntity, MemberEntity
from messenger.proto.xmpp.gloox_constants import MESSAGE_TYPE
from messenger.proto.xmpp.wrappers import XMPPChannelData
from messenger.proto.xmpp.xmpp_items import createItem

class XMPPUserEntity(UserEntity):
    __slots__ = ('_item', '_isOnlineInBW')

    def __init__(self, databaseID, name = 'Unknown', tags = None, clanAbbrev = None, clanRole = 0, item = None):
        super(XMPPUserEntity, self).__init__(databaseID, name, tags, clanAbbrev, clanRole)
        self._item = item or createItem(databaseID)
        self._isOnlineInBW = False

    def __repr__(self):
        return 'XMPPUserEntity(dbID={0!r:s}, fullName={1:>s}, tags={2!r:s}, item={3!r:s}, isOnline={4!r:s}, clanRole={5:n})'.format(self._databaseID, self.getFullName(), self.getTags(), self._item, self.isOnline(), self._clanRole)

    def clear(self):
        self._isOnlineInBW = False
        super(XMPPUserEntity, self).clear()

    def getPersistentState(self):
        state = None
        tags = USER_TAG.filterToStore(self.getTags())
        if self._databaseID and (self._item.isTrusted() or tags):
            state = (self._name, self._item.getItemType(), tags if tags else None)
        return state

    def setPersistentState(self, state):
        result = False
        if len(state) == 3:
            self._name, itemType, tags = state
            self._item = createItem(self._databaseID, itemType, trusted=False)
            if tags:
                self.addTags(tags)
            result = True
        return result

    def getProtoType(self):
        return PROTO_TYPE.XMPP

    def setSharedProps(self, other):
        result = super(XMPPUserEntity, self).setSharedProps(other)
        if result and other.getProtoType() == PROTO_TYPE.XMPP:
            if USER_TAG.CACHED in self.getTags():
                self.update(name=other.getName(), item=other.getItem())
            elif USER_TAG.CACHED in other.getTags() and other.isMuted():
                self.addTags({USER_TAG.MUTED})
        if USER_TAG.CLAN_MEMBER in self._tags:
            self._isOnlineInBW = other.isOnline()
        return result

    def getTags(self):
        tags = super(XMPPUserEntity, self).getTags()
        tags.update(self._item.getTags())
        return tags

    def removeTags(self, tags):
        super(XMPPUserEntity, self).removeTags(tags)
        if self._item.removeTags(tags):
            self._item = createItem(self._databaseID)

    def getGroups(self):
        return self._item.getGroups()

    def isOnline(self):
        return self._item.isOnline(self._isOnlineInBW)

    def update(self, **kwargs):
        if 'item' in kwargs:
            self._item = self._item.replace(kwargs['item'])
        if 'isOnline' in kwargs and USER_TAG.CLAN_MEMBER in self._tags:
            self._isOnlineInBW = kwargs['isOnline']
        if 'noClan' in kwargs and kwargs['noClan']:
            self._isOnlineInBW = False
        self._item.update(**kwargs)
        super(XMPPUserEntity, self).update(**kwargs)

    def getJID(self):
        return self._item.getJID()

    def getSubscription(self):
        return self._item.getSubscription()

    def getItemType(self):
        return self._item.getItemType()

    def getItem(self):
        return self._item


class _XMPPChannelEntity(ChannelEntity):
    __slots__ = ('_jid',)

    def __init__(self, jid, data):
        super(_XMPPChannelEntity, self).__init__(data)
        self._jid = jid

    def getID(self):
        return self._jid

    def getProtoType(self):
        return PROTO_TYPE.XMPP


class XMPPChatChannelEntity(_XMPPChannelEntity):

    def __init__(self, jid, name = ''):
        super(XMPPChatChannelEntity, self).__init__(str(jid), XMPPChannelData(name, MESSAGE_TYPE.CHAT))

    def getPersistentState(self):
        state = None
        if self._history:
            state = (tuple(self._data), list(self._history)[-10:])
        return state

    def setPersistentState(self, state):
        result = False
        if len(state) == 2:
            data, history = state
            self._data = XMPPChannelData(*data)
            self._history = deque(history, MESSAGES_HISTORY_MAX_LEN)
            result = True
        return result

    def isPrivate(self):
        return True

    def getName(self):
        return self._data.name

    def getFullName(self):
        return self.getName()

    def setJoined(self, isJoined):
        self._isJoined = isJoined
        self.onConnectStateChanged(self)


class XMPPMemberEntity(MemberEntity):

    def getProtoType(self):
        return PROTO_TYPE.XMPP

    def setOnline(self, value):
        self.setStatus(value)

    def isOnline(self):
        return self.getStatus()
