var ISSChatApp = angular.module('ISSChatApp', []);


ISSChatApp.controller('ChatController', function($scope){
    
    var socket = io.connect('https://' + document.domain + ':' + location.port + '/iss');
    
    $scope.messages = [];
    $scope.searches = [];
    $scope.roster = [];
    
    socket.on('message', function(msg){
        $scope.messages.push(msg);
        $scope.$apply();
        var elem = document.getElementById('msgpane');
        elem.scrollTop = elem.scrollHeight;
        
    });

    socket.on('connect', function (){
        console.log('connected');
        document.getElementById('formpane').style.visibility="hidden";
    });
    
    socket.on('logged', function(userdata){
          document.getElementById('loginbox').style.visibility="hidden";
          document.getElementById('accountbox').style.visibility="hidden";
          document.getElementById('formpane').style.visibility="visible";
          console.log("logged in!");
    });
    
    socket.on('searched', function(searchedMessage){
        console.log(searchedMessage);
        $scope.searches.push(searchedMessage);
        $scope.$apply();
        var elem = document.getElementById('srchpane');
        elem.scrollTop = elem.scrollHeight;
    });
    
    
  /*  socket.on('roster', function (names) {
          $scope.roster = names;
          $scope.$apply();
        }); */
    
    $scope.login = function(){
          console.log("Trying to log in");
          var un = $scope.username;
          var pw = $scope.password;
          socket.emit('login', un, pw);
    };
    
    $scope.account = function(){
          console.log("Trying to make account");
          var un = $scope.usernamegen;
          var pw = $scope.passwordgen;
          var room2 = $scope.room2;
          var room3 = $scope.room3;
          socket.emit('account', un, pw, room2, room3);
    };
    
    $scope.submitText = function(){
        console.log("trying to send message");
        var messageSending = $scope.currentText;
        $scope.currentText = null;
        socket.emit('message', messageSending);
    };
    
    $scope.searchText = function(){
        console.log("Searching");
        var searchSending = $scope.searchValue;
        socket.emit('searching', searchSending);
        $scope.searchValue = null;
        $scope.searches = [];
        
    };
    
    $scope.changeRoom1 = function()
        {
          $scope.messages = [];
          var new_room = "room1";
          console.log(new_room);
          socket.emit('changeRoom', new_room)
        }
    $scope.changeRoom2 = function()
        {
          $scope.messages = [];    
          var new_room = "room2";
          console.log(new_room);
          socket.emit('changeRoom', new_room)
        }
    $scope.changeRoom3 = function()
        {
            $scope.messages = [];
          var new_room = "room3";
          console.log(new_room);
          socket.emit('changeRoom', new_room)
        }
    
});