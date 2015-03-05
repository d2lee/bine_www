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

bineApp.controller('friendListControl', ['$scope', 'Friends', 'Users', '$http', 'authService', function ($scope, Friends, Users, $http, authService) {

    $scope.init = function () {

        $scope.user = authService.get_user();
        $scope.fetch_unconfirmed_friends();
    }

    $scope.fetch_confirmed_friends = function () {
        $scope.current_menu = "menu1";

        $scope.loading = true;
        $scope.friends = Friends.get_confirmed_friends(null, function () {
            $scope.loading = false;
        }, function () {
            $scope.loading = false;
        });
    }

    $scope.fetch_unconfirmed_friends = function () {
        $scope.current_menu = "menu2";
        $scope.loading = true;
        $scope.friends = Friends.get_waiting_friends(null, function () {
            $scope.request_friends = Friends.get_requesting_friends(null, function () {
                $scope.loading = false;
            }, function () {
                $scope.loading = false;
            });

        }, function () {
            $scope.loading = false;
        });


    }

    $scope.fetch_recommended_friends = function () {
        $scope.current_menu = "menu3";
        $scope.loading = true;
        $scope.friends = Friends.get_recommended_friends(null, function () {
            $scope.loading = false;
        }, function () {
            $scope.loading = false;
        });
    }

    $scope.search_friends = function () {
        if (!$scope.friend_form.$valid)
            return;

        var username = $scope.username;
        $scope.friends = Users.query({q: username});
    }

    $scope.add_friend = function (friend, index) {
        var new_friend = new Friends({friend: friend.id});
        new_friend.$save(null, function () {
            alert(friend.fullname + "님에게 친구 요청을 하였습니다.");
            $scope.friends.splice(index, 1);
        });

    }

    $scope.remove_friend = function (friend, index) {
        friend.$delete(null, function () {
            alert(friend.fullname + "님을 친구목록에서 삭제하였습니다.");
            $scope.friends.splice(index, 1);
        })
    }

    $scope.confirm_friend = function (friend, index) {
        friend.$confirm_friend();
        $scope.friends.splice(index, 1);
    }

    $scope.init();
}]);