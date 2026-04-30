def choose_move(observation):
    w=observation.get('grid_width',8); h=observation.get('grid_height',8)
    sx,sy=observation.get('self_position',[0,0]); ox,oy=observation.get('opponent_position',[0,0])
    resources=observation.get('resources',[]); obstacles=set(tuple(p) for p in observation.get('obstacles',[]))
    def dist(a,b,c,d): 
        dx=abs(a-c); dy=abs(b-d); 
        return dx if dx>dy else dy  # Chebyshev for 8-dir
    if resources:
        best=None; bestv=-10**9; 
        for rx,ry in resources:
            md=dist(sx,sy,rx,ry); od=dist(ox,oy,rx,ry)
            v=(od-md)*10 - md  # prefer resources opponent can't reach as quickly
            if v>bestv or (v==bestv and (md<best[0] if best else True)):
                bestv=v; best=(md,rx,ry)
        _,tx,ty=best
    else:
        tx,ty = (w-1,0) if (sx+sy)<= (w-1 - sx + oy) else (0,h-1)

    deltas=[(-1,-1),(-1,0),(-1,1),(0,-1),(0,0),(0,1),(1,-1),(1,0),(1,1)]
    def inb(x,y): return 0<=x<w and 0<=y<h
    best_move=(0,0); best_score=-10**18
    oppd=dist(sx,sy,ox,oy)
    for dx,dy in deltas:
        nx,ny=sx+dx,sy+dy
        if not inb(nx,ny): 
            continue
        if (nx,ny) in obstacles:
            continue
        nd=dist(nx,ny,tx,ty)
        od=dist(nx,ny,ox,oy)
        step=-nd*10 + od  # closer to target, farther from opponent
        if resources and (nx,ny) in set(tuple(p) for p in resources):
            step += 500
        # small obstacle-aware nudge: discourage moves that get "stuck" adjacent to obstacles
        adj=0
        for ax,ay in deltas:
            ex,ey=nx+ax,ny+ay
            if inb(ex,ey) and (ex,ey) in obstacles:
                adj+=1
        step -= adj*2
        # if we're currently not doing well, choose more aggressive opponent separation
        if observation.get('turn_index',0)%2==1 and oppd<=3:
            step += od*3
        if step>best_score or (step==best_score and (dx,dy)<best_move):
            best_score=step; best_move=(dx,dy)
    return [int(best_move[0]), int(best_move[1])]