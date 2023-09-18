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
    for lay in layer:
        figures = glob.glob(os.path.join(dir, f'*{lay}*.png'))

        frames = []
        for fig in figures:
            print(f'reading and appending {fig}')
            figure = imageio.imread(os.path.join(fig))
            frames.append(figure)
        print('all frames appended')
        print('saving GIF')
        case = f'{dir}'.split('_')[-1]
        imageio.mimsave(os.path.join(output_dir,f'Conc_{case}_{lay}.gif'), frames, fps = 5)
        print('finished saving GIF!')