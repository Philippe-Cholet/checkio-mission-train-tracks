requirejs(['ext_editor_io', 'jquery_190', 'raphael_210'],
    function (extIO, $) {
        function trainTracksAnimation(tgt_node, data) {

            if (!data || !data.ext) {
                return
            }

            // hide right-answer
            $(tgt_node.parentNode).find(".answer").remove()

            /*----------------------------------------------*
             *
             * attr
             *
             *----------------------------------------------*/
            const attr = {
                railway: {
                    'stroke-width': '1px',
                },
                rail: {
                    'stroke-width': '0.1px',
                    'fill': '#FABA00',
                },
                init_rail: {
                    'stroke-width': '0.1px',
                    'fill': '#F0801A',
                },
                plain: {
                    'stroke-width': '0.1px',
                    'fill': '#82D1F5',
                },
                number: {
                    'color': 'black',
                    'font-size': '16px',
                    'font-weight': 'bold',
                },
                number_scale: {
                    'fill': 'red',
                    'font-size': '16px',
                    'font-weight': 'bold',
                },
                grid: {
                    'stroke-width': '1px',
                    'stroke': '#82D1F5',
                },
            }

            /*----------------------------------------------*
             *
             * values
             *
             *----------------------------------------------*/
            const ip = data.in

            const start = ip[2][0]*100 + ip[2][1]
            const end = ip[3][0]*100 + ip[3][1]
            const rows = ip[0]
            const columns = ip[1]
            const output = data.out
            const constraints = {}

            const reg = /\([^(]+/g
            const reg_k = /\d+/g
            const reg_v = /[NEWS]/g
            ip[4].match(reg).forEach(m=>{
                const nums = m.match(reg_k).map(x=>Number(x))
                const key = nums[0]*100+nums[1]
                const values = m.match(reg_v)
                constraints[key] = values
            })

            const width = columns.length
            const height = rows.length

            const grid_size_px = 300
            const unit = 300 / Math.max(width, height)
            const os = 30

            const [error_msg, _] = data.ext.result_addon
            const result = data.ext.result

            /*----------------------------------------------*
             *
             * paper
             *
             *----------------------------------------------*/
            const paper = Raphael(tgt_node, unit*width+os*2, unit*height+os*2, 0, 0)

            /*----------------------------------------------*
             *
             * draw grid, number
             *
             *----------------------------------------------*/
            // background rect
            paper.rect(os, os, unit*width, unit*height).attr(attr.plain)
            const font_size = {'font-size': Math.max(5, 16*(8/Math.max(height, width)))}

            // horizontal
            for (let i = 0; i <= height; i += 1) {
                paper.path(['M', os, i*unit+os, 'h', grid_size_px]+os).attr(attr.plain)
                if (i != height) {
                    paper.text(os+unit*width+os/2, (i+0.5)*unit+os, rows[i]).attr(
                        attr.number).attr(font_size)
                    if (! result) {
                        paper.text(os/2, (i+0.5)*unit+os, i).attr(attr.number_scale).attr(font_size)
                    }
                }
                if (i == ip[2][0] && result) {
                    paper.text(os/2, (i+0.5)*unit+os, 'A').attr(attr.number).attr(
                        {'font-size': Math.max(5, 16*(8/Math.max(height, width)))})
                }
            }

            // vertical
            for (let i = 0; i <= width; i += 1) {
                paper.path(['M', i*unit+os, 0, 'v', unit*height+os]).attr(attr.plain)
                if (i != width) {
                    paper.text((i+0.5)*unit+os, 0+os/2, columns[i]).attr(attr.number).attr(font_size)
                    if (! result) {
                        paper.text((i+0.5)*unit+os, os+unit*height+os/2, i).attr(
                            attr.number_scale).attr(font_size)
                    }
                }
                if (i == ip[3][1] && result) {
                    paper.text((i+0.5)*unit+os, os+unit*height+os/2, 'B').attr(attr.number).attr(font_size)
                }
            }

            /*----------------------------------------------*
             *
             * draw route
             *
             *----------------------------------------------*/
            const opposite = {N: 'S', S: 'N', W: 'E', E: 'W'}
            const dir_mod = {N: [-1, 0], S: [1, 0], W: [0, -1], E: [0, 1]}
            const dm = {
                'N': {x: 0.5, y: 0},
                'S': {x: 0.5, y: 1},
                'W': {x: 0, y: 0.5},
                'E': {x: 1, y: 0.5},
            }
            const arc = {
                'NW': [0, 1],
                'EN': [0, 1],
                'ES': [0, 0],
                'SW': [0, 0],
            }
            if (String(output).match(/^[NSEW]+$/)) {
                let [ny, nx] = ip[2]
                let prev_dir = 'E'
                output.split('').forEach(next_dir=>{
                    let dirs = [next_dir]
                    dirs.push(opposite[prev_dir])
                    if (ny >= 0 && ny < height && nx >= 0 && nx < width) {
                        paper.rect(nx*unit+os, ny*unit+os, unit, unit).attr(attr.rail)
                        draw_rail(ny, nx, dirs)
                    }
                    const [dy, dx] = dir_mod[next_dir]
                    ny += dy
                    nx += dx
                    prev_dir = next_dir
                })
            }

            /*----------------------------------------------*
             *
             * draw constraints
             *
             *----------------------------------------------*/
            for (const co in constraints) {
                const [y, x] = [Math.floor(co/100), co % 100]
                paper.rect(x*unit+os, y*unit+os, unit, unit).attr(attr.init_rail)
                let dirs = constraints[co]
                if (co == start) {
                    dirs.push('W')
                }
                if (co == end) {
                    dirs.push('S')
                }
                draw_rail(y, x, dirs)
            }

            /*----------------------------------------------*
             *
             * draw rail (function)
             *
             *----------------------------------------------*/
            function draw_rail(y, x, dirs) {
                dirs.sort()
                const [d1, d2] = dirs
                const [x1, y1] = [(x+dm[d1].x)*unit+os, (y+dm[d1].y)*unit+os]
                const [x2, y2] = [(x+dm[d2].x)*unit+os, (y+dm[d2].y)*unit+os]
                const r = unit/2
                const dirs_join = dirs.join('')

                // straight
                if (['NS', 'EW'].includes(dirs_join)) {
                    paper.path([
                        'M', x1, y1,
                        'L', x2, y2,
                    ]).attr(attr.railway).attr({'stroke-width': Math.max(1, 2*(8/width))})

                // curve
                } else {
                    const [a, b] = arc[dirs_join]
                    paper.path([
                        'M', x1, y1,
                        'A', r, r, 45, a, b, x2, y2,
                    ]).attr(attr.railway).attr({'stroke-width': Math.max(1, 2*(8/width))})
                }
            }

            /*----------------------------------------------*
             *
             * message
             *
             *----------------------------------------------*/
            if (!data.ext.result) {
                $(tgt_node).addClass('output').prepend(
                    '<div>' + error_msg+ '<br/><br/></div>').css(
                        {'border': '0','display': 'block',})
            }
        }
        var $tryit;
        var io = new extIO({
            multipleArguments: true,
            functions: {
                python: 'train_tracks',
                // js: 'trainTracks'
            },
            animation: function($expl, data){
                trainTracksAnimation(
                    $expl[0],
                    data,
                );
            }
        });
        io.start();
    }
);
