bineApp.controller('friendConfirmedListControl', ['$scope', '$http', 'authService', function ($scope, $http, authService) {

    // check the authentication
    if (!authService.check_auth_and_set_user($scope)) {
        return;
    }

    $scope.load_friend_list = function () {
        $http.get('/api/friend/?status=Y').success(function (data) {
            $scope.friends = data;
        });
    }

    $scope.remove_friend = function (friend, index) {
        var url = "/api/friend/" + friend.id + "/";

        $http.delete(url).success(function (data) {
            alert(friend.fullname + "님을 친구목록에서 삭제하였습니다.");
            $scope.friends.splice(index, 1);
        });
    }

    $scope.load_friend_list();
}]);

bineApp.controller('friendUnconfirmedListControl', ['$scope', '$http', 'authService', function ($scope, $http, authService) {

    // check the authentication
    if (!authService.check_auth_and_set_user($scope)) {
        return;
    }

    $scope.load_friend_list = function () {
        $http.get('/api/friend/?status=N').success(function (data) {
            $scope.friends = data;
        });
    }

    $scope.confirm_friend = function (friend, index) {
        var url = "/api/friend/";
        var data = {
            'friend': friend.id,
            'status': 'Y'
        }

        $http.put(url, data).success(function (data) {
            alert(friend.fullname + "님을 친구목록에 추가하였습니다.");
            $scope.friends.splice(index, 1);
        });
    }

    $scope.unconfirm_friend = function (friend, index) {
        var url = "/api/friend/";
        var data = {
            'friend': friend.id,
            'status': 'N'
        }

        $http.put(url, data).success(function (data) {
            alert(friend.fullname + "님을 친구 목록에서 제외하였습니다.");
            $scope.friends.splice(index, 1);
        });
    }

    $scope.load_friend_list();
}]);


bineApp.controller('friendSearchControl', ['$scope', '$http', 'authService', function ($scope, $http, authService) {

    // check the authentication
    if (!authService.check_auth_and_set_user($scope)) {
        return;
    }

    $scope.search_friend = function () {
        var url = "/api/friend/search/?q=" + $scope.friend_query;
        $http.get(url).success(function (data) {
            $scope.search_friends = data;
        });
    }

    $scope.add_friend = function (friend, index) {
        var url = "/api/friend/";
        var data = {'friend': friend.id};

        $http.post(url, data).success(function (data) {
            alert(friend.fullname + "님을 친구로 등록하였습니다.");
            $scope.search_friends.splice(index, 1);
        });
    }
}]);

bineApp.controller('friendRecommendControl', ['$scope', '$http', 'authService', function ($scope, $http, authService) {

    // check the authentication
    if (!authService.check_auth_and_set_user($scope)) {
        return;
    }

    $scope.load_friend_list = function () {
        $http.get('/api/friend/recommend/').success(function (data) {
            $scope.friends = data;
        });
    }

    $scope.add_friend = function (friend, index) {
        var url = "/api/friend/";
        var data = {'friend': friend.id};

        $http.post(url, data).success(function (data) {
            alert(friend.fullname + "님을 친구로 등록하였습니다.");
            $scope.search_friends.splice(index, 1);
        });
    }

    $scope.load_friend_list();
}]);