var app = angular.module('home',[])


app.config(function($interpolateProvider) {
  $interpolateProvider.startSymbol('[$');
  $interpolateProvider.endSymbol('$]');
});
app.controller('IndexControler',function($scope){
     $scope.greeting = "hello";
     $scope.option = [
         1,2,3,4,5,6,7,8,9,0
     ];
     
     $scope.band = [
       'iphone','nokia','huawei','xiaomi','yijia','meizu','chuizi'  
     ];
});