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

app.controller("NodesController",function($scope,$http){
    $scope.nodes = [
        {   
            role:"master",
            ip:"10.0.0.1",
            port:9898,
            qps:10,
            is_started:false,
            is_paused:true,
        },        
        {
            role:"slave",
            ip:"10.0.0.2",
            port:1808,
            qps:100,
            is_started:false,
            is_paused:true,            
        },        
    ];

    $scope.locuststart = function(index){
        //启动运行
       $scope.nodes[index].is_started=true;
        $http({
            method:'POST',
            url:'/locust_start/1',
            data:{'send_data':1},
        }).success(function(data,header,config,status){
            $scope.nodes[index].is_started=true;         
        }).error(function(data,header,config,status){          
        });       
    };

    $scope.locuststop = function(index){
        //停止运行
       $scope.nodes[index].is_started=false;
    };
    
    $scope.locustpause = function(index){
        // 暂停运行
        $http({
            method:'POST',
            url:'/locust_pause/1',
            data:{'send_data':1},
        }).success(function(data,header,config,status){
            $scope.nodes[index].is_paused=true;           
        }).error(function(data,header,config,status){          
        });

    };
    
    $scope.locustresume = function(index){
        // 恢复运行
        $http({
            method:'POST',
            url:'/locust_resume/1',
            data:{'send_data':1},
        }).success(function(data,header,config,status){
            $scope.nodes[index].is_paused=false;           
        }).error(function(data,header,config,status){          
        });
    };        
    
    
});

app.controller("SysInfoController",function($scope,$http,$interval){
    
    $scope.queue_length = 0;
    $scope.auto_refreshing="#FFF";
    
    var see_queue_len = function(){
        $http({
            method:"GET",
            url:"/sysinfo",
        }).success(function(data,header,config,status){
            $scope.queue_length = data.queue_length;
        }).error(function(data,header,config,status){
            //error accours 
        });         
    };
    
    var tracing;

    $scope.refresh_tracing = function(){
        see_queue_len();
    };
    
    $scope.start_tracing = function(){
       $scope.auto_refreshing = "#eac100";
       tracing = $interval(see_queue_len,2000);
    };
    
    $scope.stop_tracing = function(){
        $scope.auto_refreshing = "#FFF";
        if(tracing){
          $interval.cancel(tracing);  
        }
        
    };
        
    $scope.refresh_tracing();
});