def choose_move(observation):
    w=observation["grid_width"]; h=observation["grid_height"]
    sx,sy=observation["self_position"]; ox,oy=observation["opponent_position"]
    resources=observation.get("resources",[]); obstacles=set(tuple(p) for p in observation.get("obstacles",[]))
    def inb(x,y): return 0<=x<w and 0<=y<h
    if not resources:
        best=[0,0]; bd=10**9
        for dx in (-1,0,1):
            for dy in (-1,0,1):
                nx,ny=sx+dx,sy+dy
                if not inb(nx,ny) or (nx,ny) in obstacles: 
                    continue
                d=abs(nx-ox)+abs(ny-oy)
                if d>bd or (d==bd and (dx,dy)==(0,0)): pass
        return [0,0]
    def nearest_dist(x,y):
        md=10**9
        for rx,ry in resources:
            d=abs(x-rx)+abs(y-ry)
            if d<md: md=d
        return md
    moves=[]
    for dx in (-1,0,1):
        for dy in (-1,0,1):
            nx,ny=sx+dx,sy+dy
            if not inb(nx,ny) or (nx,ny) in obstacles:
                continue
            dr=nearest_dist(nx,ny)
            do=abs(nx-ox)+abs(ny-oy)
            score=dr*100 - do  # primary: minimize resource distance; secondary: stay farther from opponent
            moves.append((score, dx, dy))
    if not moves:
        return [0,0]
    moves.sort(key=lambda t:(t[0], t[1], t[2]))
    return [moves[0][1], moves[0][2]]