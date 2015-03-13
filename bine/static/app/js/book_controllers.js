bineApp.controller('bookListControl', ['$scope', '$http', 'login_user', 'navbar',
    function ($scope, $http, login_user, navbar) {
    navbar.set_menu('book');

    // check the authentication
    // $scope.user = login_user.get_user();

    $scope.load_book_list = function () {
        $http.get('/api/book/').success(function (data) {
            $scope.books = data;
            $scope.noData = !$scope.books.length;
        });
    };

    $scope.load_book_list();
}]);