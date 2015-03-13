bineApp.controller('LoginControl', ['$scope', '$http', 'login_user', 'Authentication','navbar',
    function ($scope, $http, login_user, Authentication, navbar) {
        $scope.init = function() {
            navbar.set_menu('start');
            login_user.clear();
        }
        // login check
        $scope.login = function () {
            var data = {
                'username': $scope.username,
                'password': $scope.password
            }

            $scope.reset_error();
            Authentication.login(data,
                function (data) {
                    login_user.set_token_and_user_info(data);
                    $scope.http_status = 200;
                    location.href = "#/note/";
                }, function (data) {
                    $scope.http_status = data.status;
                });
        };

        $scope.reset_error = function () {
            $scope.http_status = undefined;
        }

        $scope.init();
    }])
;