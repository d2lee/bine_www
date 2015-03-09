bineApp.controller('UserControl', ['$scope', '$http', '$upload', 'authService', 'Users',
    function ($scope, $http, $upload, authService, Users) {
        $scope.init = function () {
            var user = authService.get_user();

            $scope.show_account();

            var user_id = user.id;
            $scope.init_birthday();

            $scope.user = Users.get({id: user_id}, function () {
                // initialize the birthday
                $scope.birth_year = $scope.user.birthday.substr(0, 4);
                $scope.birth_month = $scope.user.birthday.substr(5, 2);
                $scope.birth_day = $scope.user.birthday.substr(8, 2);
            });
        };

        $scope.show_account = function () {
            $scope.current_menu = 'account';
        }

        $scope.show_profile = function () {
            $scope.current_menu = 'profile';
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
            var title;

            for (var value = min; value != max; value += step) {
                // adding '0' if it's single digit
                if (value < 10) {
                    title = "0" + value;
                }
                else {
                    title = value;
                }
                // output.push({'text': title, 'value': title});
                output.push(title);
            }

            // output.push({'text': max, 'value': max});
            output.push(max);

            // returning the generated array
            return output;
        };

        $scope.init_birthday = function () {
            $scope.year_list = $scope.date_range((new Date()).getFullYear(), 1910);
            $scope.month_list = $scope.date_range(1, 12);
            $scope.day_list = $scope.date_range(1, 31);
        };

        $scope.set_sex = function (sex) {
            $scope.user.sex = sex;
        };

        // 사용자 정보를 업데이트합니다.
        $scope.update_user = function () {
            if (!$scope.user_form.$valid)
                return;

            $scope.user.birthday = $scope.birth_year + "-" + $scope.birth_month + "-" + $scope.birth_day;
            $scope.user.current_password = $scope.current_password;
            $scope.user.password = $scope.password1;

            $scope.http_status = '';
            $scope.user.$update(null, function () {
                $scope.http_status = 200;
            }, function (response) {
                $scope.user_form.current_password.$error.wrong_password = true;
                $scope.http_status = response.status;
            });
        }

        $scope.upload = function (files) {
            var file = files[0];
            var user_id = $scope.user.id;

            var url = '/api/user/' + user_id + '/?action=photo';

            if (file) {
                $upload.upload({
                    url: url,
                    file: file
                }).progress(function (evt) {
                    var progressPercentage = parseInt(100.0 * evt.loaded / evt.total);

                }).success(function (data, status, headers, config) {
                    $scope.user.photo = data.photo;
                });
            }
        }

        $scope.init();

    }
])
;