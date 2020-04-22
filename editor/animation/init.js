requirejs(['ext_editor_io', 'jquery_190'],
    function (extIO, $) {
        var $tryit;
        var io = new extIO({
            multipleArguments: true,
            functions: {
                python: 'train_tracks',
                // js: 'trainTracks'
            }
        });
        io.start();
    }
);
