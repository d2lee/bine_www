/**
 * Created by dolee on 15. 3. 6..
 */
bineApp.factory('Friends', ['$resource', function ($resource) {
    return $resource('/api/friend/:friendId/', {friendId: '@id'}, {
        'get_confirmed_friends': {method: 'GET', params: {type: 'confirm'}, isArray: true},
        'get_requesting_friends': {method: 'GET', params: {type: 'from'}, isArray: true},
        'get_waiting_friends': {method: 'GET', params: {type: 'to'}, isArray: true},
        'get_recommended_friends': {method: 'GET', params: {type: 'recommend'}, isArray: true},
        'confirm_friend': {method:'PUT'},
    }, {stripTrailingSlashes: false});
}]);

bineApp.factory('Users', ['$resource', function ($resource) {
    return $resource('/api/user/', null, {}, {stripTrailingSlashes: false});
}]);