/*
    Friend 객체
 */
bineApp.factory('Friends', ['$resource', function ($resource) {
    return $resource('/api/friend/:friendId/', {friendId: '@id'}, {
        'get_friends': {method: 'GET', params: {type: 'confirm'}, isArray: true},
        'get_friends_by_me': {method: 'GET', params: {type: 'me'}, isArray: true},
        'get_friends_by_others': {method: 'GET', params: {type: 'others'}, isArray: true},
        'get_recommended_friends': {method: 'GET', params: {type: 'recommend'}, isArray: true},
        'approve_friend': {method: 'PUT', params: {status:'A'}},
        'reject_friend': {method: 'PUT', params: {status:'R'}}
    }, {stripTrailingSlashes: false});
}]);

/*
    User 객체
 */
bineApp.factory('Users', ['$resource', function ($resource) {
    return $resource('/api/user/', null, {}, {stripTrailingSlashes: false});
}]);

/*
    BookNote 객체
 */
bineApp.factory('BookNotes', ['$resource', function ($resource) {
    return $resource('/api/note/:noteId/', {noteId: '@id'}, {
        'get_notes_by_all': {method: 'GET', params: {type: 'all'}, isArray: true},
        'get_notes_by_me': {method: 'GET', params: {type: 'me'}, isArray: true},
        'get_notes_by_friend': {method: 'GET', params: {type: 'friend'}, isArray: true},
        'get_new_notes': {method: 'GET', params: {type: 'new'}, isArray: true},
        'create_note': {method: 'POST', params: {status:'A'}},
        'delete_note': {method: 'DELETE', params: {status:'R'}},
        'edit_note': {method: 'POST', params: {status:'R'}}
    }, {stripTrailingSlashes: false});
}]);