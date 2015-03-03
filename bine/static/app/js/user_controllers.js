bineApp.controller('UserControl', ['$scope', '$http', 'authService',
    function ($scope, $http, authService) {
        $scope.init = function () {

            // check the authentication
            if (!authService.check_auth_and_set_user($scope)) {
                return;
            }
        }

        $scope.init();
    }
]);