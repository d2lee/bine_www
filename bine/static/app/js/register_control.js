bineApp.controller('RegisterControl', ['$scope', '$http', 'login_user', 'Authentication', 'navbar',
    function ($scope, $http, login_user, Authentication, navbar) {
        $scope.init = function () {
            navbar.set_menu('start');
            login_user.clear();
            $scope.step = "step1";
            $scope.init_birthday();
            $scope.page_title = "Bine 회원가입";
        }

        /*
         사용자 아이디 중복 검사
         */
        $scope.check_user_duplication = function () {
            if (!$scope.username) {
                return;
            }

            var data = {
                'username': $scope.username
            }
            Authentication.check(data,
                function (data) {
                    $scope.user_duplicated = true;

                },
                function (data) {
                    $scope.user_duplicated = false;
                })
        };

        /*
         새 사용자 등록 함수
         */
        $scope.register = function () {
            if (!$scope.reg_form.$valid && ($scope.user_duplicated == false))
                return;

            var url = "/api/user/register/";

            $scope.make_birthday();

            var data = {
                'username': $scope.username,
                'fullname': $scope.fullname,
                'email': $scope.email,
                'birthday': $scope.birthday,
                'sex': $scope.sex,
                'password': $scope.password1
            };

            $scope.http_status = undefined;

            $scope.step = "step1";
            Authentication.register(data, function (data) {
                login_user.set_token_and_user_info(data);
                $scope.step = "step2";
                $scope.page_title = "Bine 회원가입 완료";
                $scope.http_status = data.status;

            }, function (data) {
                $scope.step = "step1";
                $scope.http_status = data.status;
            });
        };

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
        };

        $scope.equal_password = function () {
            return $scope.password1 == $scope.password2;
        };

        $scope.set_sex = function (sex) {
            $scope.sex = sex;
        };

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
        };

        $scope.init();
    }])
;