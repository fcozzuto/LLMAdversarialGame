def choose_move(observation):
    w=observation["grid_width"]; h=observation["grid_height"]
    my=observation["self_position"]; op=observation["opponent_position"]
    res=observation["resources"]; obs=set(tuple(p) for p in observation["obstacles"])
    x0,y0=my; ox,oy=op
    moves=[(-1,-1),(-1,0),(-1,1),(0,-1),(0,0),(0,1),(1,-1),(1,0),(1,1)]
    def inb(x,y): return 0<=x<w and 0<=y<h
    def dist(a,b): return abs(a[0]-b[0])+abs(a[1]-b[1])
    best=None; bestv=-10**9
    for dx,dy in moves:
        nx,ny=x0+dx,y0+dy
        if not inb(nx,ny) or (nx,ny) in obs: 
            continue
        myd=(nx,ny)
        v=0.0
        if res:
            best_res_score=-10**9
            for rx,ry in res:
                d1=dist(myd,(rx,ry)); d2=dist((ox,oy),(rx,ry))
                # Prefer resources I can reach sooner than opponent; also prefer closer routes
                s=(d2-d1)*10 - d1*0.3
                if s>best_res_score: best_res_score=s
            v=best_res_score
            # slight pressure to stay closer to the most contested direction
            v-=dist(myd,(ox,oy))*0.05
        else:
            v=-dist(myd,(ox,oy))
        if v>bestv or (v==bestv and (dx,dy)<best):
            bestv=v; best=(dx,dy)
    if best is None: 
        return [0,0]
    return [best[0],best[1]]