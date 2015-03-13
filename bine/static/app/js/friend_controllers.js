bineApp.controller('friendListControl', ['$scope', 'Friends', 'Users', '$http', 'authService', function ($scope, Friends, Users, $http, authService) {

    $scope.init = function () {
        $scope.navbarMenu = 'friend';

        $scope.user = authService.get_user();
        $scope.fetch_unconfirmed_friends();
    };

    $scope.fetch_confirmed_friends = function () {
        $scope.current_menu = "menu1";

        $scope.loading = true;
        $scope.friends = Friends.get_friends(null, function () {
            $scope.loading = false;
        }, function () {
            $scope.loading = false;
        });
    };

    $scope.fetch_unconfirmed_friends = function () {
        $scope.current_menu = "menu2";
        $scope.loading = true;
        $scope.friends = Friends.get_friends_by_others(null, function () {
            $scope.request_friends = Friends.get_friends_by_me(null, function () {
                $scope.loading = false;
            }, function () {
                $scope.loading = false;
            });

        }, function () {
            $scope.loading = false;
        });
    };

    $scope.fetch_recommended_friends = function () {
        $scope.current_menu = "menu3";
        $scope.loading = true;
        $scope.friends = Friends.get_recommended_friends(null, function () {
            $scope.loading = false;
        }, function () {
            $scope.loading = false;
        });
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