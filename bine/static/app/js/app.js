var bineApp = angular.module('bineApp', ['ngRoute', 'ngResource', 'ngCookies', 'ngSanitize',
    'angular-jwt', 'angularFileUpload']);

bineApp.directive('repeatDone', function () {
    return function (scope, element, attrs) {
        if (scope.$last) { // all are rendered
            scope.$eval(attrs.repeatDone);
        }
    }
});

bineApp.config(['$routeProvider', function ($routeProvider) {
    $routeProvider.when('/note/', {
        templateUrl: '/static/app/note_list.html',
        controller: 'NoteListControl'
    }).when('/login/', {
        templateUrl: '/static/app/login.html',
        controller: 'LoginControl'
    }).when('/register/', {
        templateUrl: '/static/app/register.html',
        controller: 'RegisterControl'
    }).when('/user/', {
        templateUrl: '/static/app/user.html',
        controller: 'UserControl'
    }).when('/note/new/', {
        templateUrl: '/static/app/note_form.html',
        controller: 'NoteNewControl'
    }).when('/note/:note_id/', {
        templateUrl: '/static/app/note_detail.html',
        controller: 'NoteDetailControl'
    }).when('/book/', {
        templateUrl: '/static/app/book_list.html',
        controller: 'bookListControl'
    }).when('/friend/', {
        templateUrl: '/static/app/friend_list.html',
        controller: 'friendListControl'
    }).otherwise({
        redirectTo: '/note/'
    });
}]);


bineApp.service('authService', ['$http', '$window', '$rootScope', 'jwtHelper',
    function ($http, $window, $rootScope, jwtHelper) {

        this.clear = function () {
            this.set_user(null);
            this.set_token(null);
        };

        this.check_auth_and_set_user = function ($scope) {
            $scope.user = $rootScope.user;
            return true;
        };

        this.isTokenExpired = function () {
            var token = this.get_token();
            if (!token)
                return true;

            var isExpired = true;

            try {
                isExpired = jwtHelper.isTokenExpired(token);
            }
            catch (e) {
            }

            return isExpired;
        };

        this.refresh_token_if_expired_soon = function () {
            var token = this.get_token();

            var datetime = jwtHelper.getTokenExpirationDate(token);
            var datetime = new Date(datetime).getTime();

            var now = new Date().getTime();

            var milisec_diff;
            if (datetime < now) {
                milisec_diff = now - datetime;
            } else {
                milisec_diff = datetime - now;
            }

            var mins = Math.floor(milisec_diff / 1000 / 60);

            if (mins <= 5) {
                var data = {'token': token};
                var url = "/api/auth/refresh_token/";

                $http.post(url, data).success(function (data) {
                    $window.sessionStorage.token = data.token;
                }).error(function () {

                })
            }
        };

        this.set_token_and_user_info = function (data) {
            this.set_token(data.token);
            this.set_user(data.user);
        };

        this.set_token = function (token) {
            if (token)
                $window.sessionStorage.token = token;
            else
                delete $window.sessionStorage.token;
        };

        this.get_token = function () {
            return $window.sessionStorage.token;
        };

        this.get_user = function () {
            return angular.fromJson($window.sessionStorage.user);
        };

        this.set_user = function (user) {
            if (user)
                $window.sessionStorage.user = angular.toJson(user);
            else
                delete $window.sessionStorage.user;
        }
    }]);

bineApp.config(function Config($httpProvider, jwtInterceptorProvider) {
    jwtInterceptorProvider.authPrefix = 'JWT ';
    jwtInterceptorProvider.tokenGetter = ['authService',
        function (authService) {
            return authService.get_token();
        }];

    $httpProvider.interceptors.push('jwtInterceptor');
});


// 페이지가 변경될 떄마다 token 만료 시간이 얼마남지 않았으면 새로 refresh하고 만료되었으면 login화면으로 이동한다.
bineApp.run(['$location', '$rootScope', 'authService', function ($location, $rootScope, authService) {
    $rootScope.$on("$routeChangeStart", function (event, next, current) {
        if (this.is_skip_url(next))
            return;

        if (!authService.get_token()) {
            $location.path('/login/');
        }
        else {
            if (authService.isTokenExpired()) {
                event.preventDefault();
                $rootScope.$evalAsync(function () {
                    $location.path('/login/');
                });
            }
            else {
                authService.refresh_token_if_expired_soon();

                // $rootScope.user = authService.get_user();
            }
        }
    });

    this.is_skip_url = function (next) {
        return next.$$route && (next.$$route.originalPath == '/register/' || next.$$route.originalPath == '/login/');
    }
}]);


bineApp.filter('truncate', function () {
    return function (content, maxCharacters) {
        if (content == null)
            return "";

        content = "" + content;
        content = content.trim();
        if (content.length <= maxCharacters)
            return content;

        content = content.substring(0, maxCharacters);
        var lastSpace = content.lastIndexOf(" ");
        if (lastSpace > -1)
            content = content.substr(0, lastSpace);

        return content + '...';
    };
});

bineApp.filter('photo', function () {
    return function (content, sex) {
        if (content && content != null) {
            return '/media/' + content;
        }
        else if (sex == 'M') {
            return '/static/app/images/male.jpg';
        }
        else if (sex == 'F') {
            return '/static/app/images/female.jpg';
        }
    };
});
