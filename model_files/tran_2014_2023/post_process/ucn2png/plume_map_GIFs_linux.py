import os
import imageio
import glob


cwd = os.getcwd()
fig_dir = os.path.join(cwd, 'output', 'png')
output_dir = os.path.join(cwd, 'output', 'gif')
if not os.path.isdir(output_dir):
    os.makedirs(output_dir)

dirs = glob.glob(os.path.join(fig_dir, '*'))
print('reading from directories:')
for dir in dirs:
    print(f'{dir}')

layer = ['Lay_9', 'Lay_max']
for dir in dirs:
 #   case = f'{dir}'.split('_')[-1]
    for lay in layer:
        figures = sorted(glob.glob(os.path.join(dir, f'*{lay}*.png')))

        frames = []
        for fig in figures:
            print(f'reading and appending {fig}')
            figure = imageio.v3.imread(os.path.join(fig))
            frames.append(figure)
        print('all frames appended')
        print('saving GIF')
        case = f'{dir}'.split('_')[-1]
        imageio.v3.imwrite(os.path.join(output_dir,f'Conc_{case}_{lay}.gif'), frames)
        print(f'finished saving GIF for {dir} {lay}')
print('all done!')
