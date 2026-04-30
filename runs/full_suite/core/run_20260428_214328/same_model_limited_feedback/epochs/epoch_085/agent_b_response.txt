def choose_move(observation):
    w=observation.get("grid_width",8); h=observation.get("grid_height",8)
    sx,sy=observation["self_position"]; ox,oy=observation["opponent_position"]
    resources=observation.get("resources",[]) or []
    obstacles=observation.get("obstacles",[]) or []
    obs=set((x,y) for x,y in obstacles if 0<=x<w and 0<=y<h)
    def inb(x,y): return 0<=x<w and 0<=y<h
    def dist(a,b,c,d): 
        dx=abs(a-c); dy=abs(b-d)
        return dx if dx>dy else dy
    moves=[(-1,-1),(0,-1),(1,-1),(-1,0),(0,0),(1,0),(-1,1),(0,1),(1,1)]
    best=None; bestv=-10**9
    if not resources:
        tx=max(0,min(w-1,ox)); ty=max(0,min(h-1,oy))
        target=(tx,ty)
    else:
        target=None
        # pick resource that favors us: closer we get, farther we keep opponent
        bestt=None; besttv=10**9
        for rx,ry in resources:
            v=dist(sx,sy,rx,ry)-0.8*dist(ox,oy,rx,ry)
            if v<besttv: besttv=v; bestt=(rx,ry)
        target=bestt
    # evaluate local move
    for dx,dy in moves:
        nx,ny=sx+dx,sy+dy
        if not inb(nx,ny) or (nx,ny) in obs:
            nx,ny=sx,sy
        if resources:
            rx,ry=target
            v= -dist(nx,ny,rx,ry) + 0.6*dist(ox,oy,rx,ry)
            # also discourage letting opponent get too close
            v -= 0.15*dist(nx,ny,ox,oy)
        else:
            v= -dist(nx,ny,ox,oy)
        if v>bestv:
            bestv=v; best=(dx,dy)
    return [int(best[0]), int(best[1])]