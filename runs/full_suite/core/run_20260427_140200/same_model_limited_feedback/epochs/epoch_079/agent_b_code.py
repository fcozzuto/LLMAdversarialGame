def choose_move(observation):
    w=observation["grid_width"]; h=observation["grid_height"]
    sx,sy=observation["self_position"]; ox,oy=observation["opponent_position"]
    res=observation.get("resources") or []
    obstacles=set(tuple(p) for p in (observation.get("obstacles") or []))
    moves=[(dx,dy) for dx in (-1,0,1) for dy in (-1,0,1)]
    def clamp(x,a,b): 
        return a if x<a else b if x>b else x
    def dist2(a,b,c,d):
        dx=a-c; dy=b-d; return dx*dx+dy*dy
    if not res:
        best=(0,0); bestv=-10**18
        for dx,dy in moves:
            nx=clamp(sx+dx,0,w-1); ny=clamp(sy+dy,0,h-1)
            if (nx,ny) in obstacles: 
                continue
            v=-(dist2(nx,ny,ox,oy)) - (0.01*(nx+ny))
            if v>bestv: bestv=v; best=(dx,dy)
        return [best[0],best[1]]
    best_res=None; best_key=None
    for rx,ry in res:
        d1=dist2(sx,sy,rx,ry); d2=dist2(ox,oy,rx,ry)
        key=(d1-d2, d1)
        if best_key is None or key<best_key:
            best_key=key; best_res=(rx,ry)
    rx,ry=best_res
    best=(0,0); bestv=-10**18
    for dx,dy in moves:
        nx=clamp(sx+dx,0,w-1); ny=clamp(sy+dy,0,h-1)
        if (nx,ny) in obstacles:
            continue
        d_to=dist2(nx,ny,rx,ry)
        d_op=dist2(nx,ny,ox,oy)
        v=-d_to + 0.35*d_op
        if (nx,ny)==(rx,ry): v+=10**6
        if (dx,dy)==(0,0): v-=3
        if d_op==0: v-=10**6
        if v>bestv: bestv=v; best=(dx,dy)
    if bestv==-10**18:
        return [0,0]
    return [best[0],best[1]]