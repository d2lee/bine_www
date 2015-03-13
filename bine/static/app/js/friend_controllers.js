bineApp.controller('friendListControl', ['$scope', '$routeParams', 'Friends', 'Users','login_user', 'navbar',
    function ($scope, $routeParams, Friends, Users, login_user, navbar) {

    $scope.init = function () {
        navbar.set_menu('friend');

        var action = $routeParams.action;

        $scope.friends_state = Friends.get_friends_count();

        if (action == "m1") {
            $scope.fetch_confirmed_friends();
        }
        else if (action == "m2") {
            $scope.fetch_unconfirmed_friends();
        }
        else if (action == 'm3') {
            $scope.fetch_recommended_friends();
        }
        else {
            $scope.fetch_unconfirmed_friends();
        }
    };

    $scope.fetch_confirmed_friends = function () {
        $scope.current_menu = "m1";
        $scope.friends = Friends.get_friends();
    };

    $scope.fetch_unconfirmed_friends = function () {
        $scope.current_menu = "m2";
        $scope.friends = Friends.get_friends_by_others();
    };

    $scope.fetch_recommended_friends = function () {
        $scope.current_menu = "m3";
        $scope.friends = Friends.get_recommended_friends();
    };

    $scope.search_friends = function () {
        if (!$scope.friend_form.$valid)
            return;

        var username = $scope.username;
        $scope.friends = Users.query({q: username});
    };

    $scope.add_friend = function (friend, index) {
        var new_friend = new Friends({friend: friend.id});
        new_friend.$save(null, function () {
            alert(friend.fullname + "님에게 친구 요청을 하였습니다.");
            $scope.friends.splice(index, 1);
        });

    };

    $scope.reject_friend = function (friend, index) {
        friend.$reject_friend(null, function () {
            alert(friend.fullname + "님의 친구요청을 거절하였습니다.");
            $scope.friends.splice(index, 1);
        })
    };

    $scope.approve_friend = function (friend, index) {
        friend.$approve_friend(null, function () {
            alert(friend.fullname + "님을 친구목록에 추가하였습니다.");
            $scope.friends.splice(index, 1);
        })
    };

    $scope.delete_friend = function (friend, index) {
        friend.$delete(null, function () {
            alert(friend.fullname + "님을 친구요청을 취소했습니다.");
            $scope.request_friends.splice(index, 1);
        })
    };

    $scope.init();
}]);