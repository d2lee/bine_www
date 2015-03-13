bineApp.controller('bookListControl', ['$scope', '$http', 'authService', function ($scope, $http, authService) {
    $scope.navbarMenu = 'book';

    // check the authentication
    $scope.user = authService.get_user();

    $scope.load_book_list = function () {
        $http.get('/api/book/').success(function (data) {
            $scope.books = data;
            $scope.noData = !$scope.books.length;
        });
    };

    $scope.load_book_list();
}]);