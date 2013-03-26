Greetings yfnkm,
    
    Are you still using cast iron pans? In my day there was a bit of controversy about
their continued use since, as you probably know, they tend to get a might rusty and
unsavory after a few seasons of mistreatment at the hands of underinformed or
overworked pikans. Well, in any case, since you happen to be reading this here kitchen.py
documentation, I can only assume that you are preparing to generate a calendar for the
young folks of the day in order to make sure all the cookin' and the cleanin' gets done.

    Well, a couple a things that you should be aware of before you start I might as well
mention here up front. Most of the code that does the thing that you want is in assigner.py,
so if you don't have that in this directory or in your python path, then you are going to
have some trouble. Second thing is that assigner.py needs to use numpy, so you also have
to have that one installed.

    Last, I'll do a little explainin' about how to make this thing work. You are going to
want to write a python script that imports kitchen.py and does some important things:

1)  First you've got to generate a ConstraintsTable with all the preference information for
    the young folks and their preferred jobs. the method down below called parseCSV is for 
    doing just that, but its highly specific to the kind of google form I was using at the time.
    So, you might be wise to rewrite it to bring it up to your own highly specific standards.

2)  Second, you've got to make any appropriate changes to your constraints table that you want.
    What I used to do is select who the big cooks would be outright, and maybe make exception
    for myself as well. Then if you need to add some less standard jobs like "bread maker"
    or "Sausage Collector," then you've got to put those in too. Keep in mind that when you
    add a job, you've also got to give it someone or at least make some people acquire a taste
    for it.

3)  Third, you've got to generate a solution with the assigner module. That ain't such a
    tricky thing, but there are some important things to do. You'll notice a sort of silly
    little attribute in the Scheduler class called "extraProcessing". Well it don't really
    do that much on the whole, and you might be wonderin' why its in there at all. Well.
    It's made just for you yfnkm, 'cause its for putting in a function to combine pairs of
    young folks that only want to be on half meal plan. It so happens that just such a
    function has been added down below. Its called "combineHalfers." Now you might look at
    that function and decide it isn't quite what you expected it to be, and well, maybe
    thats true. But, it works tolerable well, and well, that works reasonable okay for me.

4)  Fourth, you've got to take a look at what you've done. Now, down there you'll see a
    another function that might come in handy. Its called printSolution, and it was 
    especially made for yours truly to see what I hath wrought. Its reasonably
    self-explanatory so I'll just suppose you'll have a gander at it yourself if it becomes
    a useful thing for you to do.

Well, thats just about the gist of it. I'll go ahead and give you an example, and some of the
accompanying files might be just be useful to ya.

                                                                        ---yfnkm of yor


