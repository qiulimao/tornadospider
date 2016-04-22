# weblocust

project weblocust aims to build a agilent web spider by using tornado

weblocust's feature

*	has simple but easy to use web user interface.
*	angularjs powers the fonted
*	tornado web flues the backend as restful server
*	the task queue use either redis or rabbitmq
*	librarys whose community are not active are not considered in this project

weblocust relys on

* Linux or MacOS
* tornado
* redis,rabbitmq
* lxml
* sqlalchemy


why tornado?
*	coroutine library
*	maturing web framework

why angularjs?

* two-way binding
* MV*C fonted framework
* nothing is better than SPA when it comes to building a control center

why lxml?

* integrate with xpath
* fast

why redis or rabbitmq ?

* fast due to datas are in memory
* by using this,weblocust has the chance to be built to a distribute system