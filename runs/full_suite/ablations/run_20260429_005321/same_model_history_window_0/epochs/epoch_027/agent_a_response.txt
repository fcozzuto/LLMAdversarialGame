def choose_move(observation):
    w=observation["grid_width"]; h=observation["grid_height"]
    sx,sy=observation["self_position"]; ox,oy=observation["opponent_position"]
    resources=observation["resources"]; obstacles=set(map(tuple,observation["obstacles"]))
    best_adv=-10**9; best_r=None
    def dist(a,b): 
        dx=abs(a[0]-b[0]); dy=abs(a[1]-b[1])
        return dx if dx>dy else dy
    for r in resources:
        if tuple(r) in obstacles: 
            continue
        myd=dist((sx,sy),r); opd=dist((ox,oy),r)
        adv=opd-myd
        if adv>best_adv or (adv==best_adv and (myd<(dist((sx,sy),best_r)) if best_r else True)):
            best_adv=adv; best_r=r
    if best_r is None:
        tx,ty=w//2,h//2
    else:
        tx,ty=best_r[0],best_r[1]
    dx0=0 if tx==sx else (1 if tx>sx else -1)
    dy0=0 if ty==sy else (1 if ty>sy else -1)
    candidates=[[dx0,dy0],[dx0,0],[0,dy0],[-dx0,dy0],[dx0,-dy0],[0,0],[1,1],[1,-1],[-1,1],[-1,-1]]
    deltas=[]
    for d in candidates:
        dx,dy=d
        if dx in (-1,0,1) and dy in (-1,0,1):
            nx=sx+dx; ny=sy+dy
            if 0<=nx<w and 0<=ny<h and (nx,ny) not in obstacles:
                deltas.append([dx,dy])
    if not deltas: 
        return [0,0]
    def d_to_target(d):
        nx=sx+d[0]; ny=sy+d[1]
        return dist((nx,ny),(tx,ty))
    deltas.sort(key=lambda d:(d_to_target(d), abs(d[0]-dx0)+abs(d[1]-dy0)))
    return deltas[0]