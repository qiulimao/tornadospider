var app = angular.module('home',[])


app.config(function($interpolateProvider) {
  $interpolateProvider.startSymbol('[$');
  $interpolateProvider.endSymbol('$]');
});

/*
app.controller('IndexControler',function($scope){
     $scope.greeting = "hello";
     $scope.option = [
         1,2,3,4,5,6,7,8,9,0
     ];
     
     $scope.band = [
       'iphone','nokia','huawei','xiaomi','yijia','meizu','chuizi'  
     ];
});

*/

/*
*
*
*/

app.controller("SystemController",function($scope,$http,$interval){
    
    $scope.nodes = [];
    $scope.tooken = 0;
    $scope.auto_refreshing = "#FFF";
    $scope.watcher = function(){
        $http({
            url:"/infocenter",
            method:"GET",
        }).success(function(data,header,config,status){
            $scope.task_queue_length = data.task_queue_length
            $scope.tooken = data.tooken;
            $scope.nodes = [];
            angular.forEach(data.nodes, function(node,index,array){
                    $scope.nodes.push(JSON.parse(node[1]));
            });
        });                
    };
    
    $scope.watcher()
    var tracing;
    
    $scope.refresh_tracing = function(){
        $scope.watcher();
    };
    
    $scope.start_tracing = function(){
        $scope.auto_refreshing = "#ea7500";
        tracing = $interval($scope.refresh_tracing,1000);
    };
    
    $scope.stop_tracing = function(){
        $scope.auto_refreshing = "#FFF";
        if (tracing){
            $interval.cancel(tracing);
        }
    };

    

    $scope.locuststart = function(index){
        //启动运行
        $http({
            method:'POST',
            url:'/locust-control',
            data:{'action':"start"},
        }).success(function(data,header,config,status){
            $scope.nodes[index].running=true;         
        }).error(function(data,header,config,status){          
        });       
    };

    $scope.locustrestart = function(index){
        //停止运行
       
        $http({
            method:'POST',
            url:'/locust-control',
            data:{'action':"restart"},
        }).success(function(data,header,config,status){
            $scope.nodes[index].running=false;        
        }).error(function(data,header,config,status){          
        });        
    };
    
    $scope.locustpause = function(index){
        // 暂停运行
        $http({
            method:'POST',
            url:'/locust-control',
            data:{'action':"pause"},
        }).success(function(data,header,config,status){
            $scope.nodes[index].paused=true;           
        }).error(function(data,header,config,status){          
        });

    };
    
    $scope.locustresume = function(index){
        // 恢复运行
        // 要获得对应的ip 和端口号
        
        $http({
            url:'/locust-control',
            method:'POST',
            data:{'action':"resume"},
        }).success(function(data,header,config,status){
            $scope.nodes[index].paused=false;           
        }).error(function(data,header,config,status){          
        });
    };
    
});