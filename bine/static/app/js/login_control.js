bineApp.controller('LoginControl', ['$scope', '$http', 'authService', 'Authentication',
    function ($scope, $http, authService, Authentication) {
        // login check
        $scope.login = function () {
            var data = {
                'username': $scope.username,
                'password': $scope.password
            }

            $scope.reset_error();
            Authentication.login(data,
                function (data) {
                    authService.set_token_and_user_info(data);
                    $scope.http_status = 200;
                    location.href = "#/note/";
                }, function (data) {
                    $scope.http_status = data.status;
                });
        };

        $scope.reset_error = function () {
            $scope.http_status = undefined;
        }
    }])
;