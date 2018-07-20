'use strict';

// check out overlap:
// https://www.w3schools.com/howto/howto_css_image_overlay.asp

// Training:
// https://becominghuman.ai/tensorflow-object-detection-api-tutorial-training-and-evaluating-custom-object-detector-ed2594afcf73
// hhttps://pythonprogramming.net/introduction-use-tensorflow-object-detection-api-tutorial/

var app = angular.module('myApp.view1', ['ngRoute']);

app.config(['$routeProvider', function($routeProvider) {
  $routeProvider.when('/view1', {
    templateUrl: 'view1/view1.html',
    controller: 'View1Ctrl'
  });
}]);

app.controller('View1Ctrl', function($scope) {
	$scope.items = [];

	var json = null;
	$.getJSON( "/data/training.json", function( data ) {
		if (data.Artic !== 'undefined') {
			var artic = data.Artic;
			var len = artic.length / 2;
			for(var i = 0; i < len; i++) {
				var articI = artic[i];
				$scope.items.push({"idx": i, "file": "thumb-img//" + articI.filt_color});
			}
			$scope.$apply();
		}
	});	
});