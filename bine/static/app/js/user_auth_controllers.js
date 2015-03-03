bineApp.controller('UserAuthControl', ['$scope', '$http', 'authService',
    function ($scope, $http, authService) {

        authService.clear();

        $scope.register_step1 = true;

        // login check
        $scope.login = function () {
            $http.post('/api/auth/login/', {
                'username': $scope.username,
                'password': $scope.password
            }).success(function (data) {
                authService.set_token_and_user_info(data);
                location.href = "#/note/";
            }).error(function (data) {
                alert('로그인이 실패했습니다. 사용자 정보를 다시 확인하십시오.');
            });
        }

        /*
         새 사용자 등록 함수
         */
        $scope.register = function () {
            if (!$scope.reg_form.$valid)
                return;

            var url = "/api/auth/register/";

            $scope.make_birthday();

            data = {
                'username': $scope.username,
                'fullname': $scope.fullname,
                'email': $scope.email,
                'birthday': $scope.birthday,
                'sex': $scope.sex,
                'password': $scope.password1,
            }

            $http.post(url, data).success(function (data) {
                authService.set_token_and_user_info(data);
                $scope.register_step1 = false;
                $scope.register_step2 = true;
            });
        }

        $scope.make_birthday = function () {
            var year = $scope.birth_year;
            var month = $scope.birth_month;
            var day = $scope.birth_day;

            if (year.v != null && month.v != null && day.v != null) {
                $scope.birthday = year.name + '-' + month.name + '-' + day.name;
            }
            else {
                $scope.birthday = '';
            }
        }

        $scope.equal_password = function () {
            return $scope.password1 == $scope.password2;
        }

        $scope.set_sex = function (sex) {
            $scope.sex = sex;
        }

        $scope.date_range = function (min, max, step) {
            // parameters validation for method overloading
            if (max == undefined) {
                max = min;
                min = 0;
            }

            step = Math.abs(step) || 1;
            if (min > max) {
                step = -step;
            }
            // building the array
            var output = [];

            for (var value = min; value != max; value += step) {
                // adding '0' if it's single digit
                if (value < 10) {
                    title = "0" + value;
                }
                else {
                    title = value;
                }
                output.push({'name': title, 'v': value});
            }

            output.push({'name': max, 'v': max});

            // returning the generated array
            return output;
        };

        $scope.init_birthday = function () {
            $scope.year_list = $scope.date_range((new Date()).getFullYear(), 1910);
            $scope.month_list = $scope.date_range(1, 12);
            $scope.day_list = $scope.date_range(1, 31);
        }

        $scope.init_birthday();

    } ]);