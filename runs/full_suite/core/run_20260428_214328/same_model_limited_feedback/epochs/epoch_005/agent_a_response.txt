def choose_move(observation):
    w=observation["grid_width"]; h=observation["grid_height"]
    sx,sy=observation["self_position"]; ox,oy=observation["opponent_position"]
    obstacles=set((x,y) for x,y in observation["obstacles"])
    resources=sorted((x,y) for x,y in observation["resources"])
    def inb(x,y): return 0<=x<w and 0<=y<h
    def dist(a,b,c,d):
        dx=a-c; dy=b-d
        return (dx*dx+dy*dy)**0.5
    if resources:
        best=None
        for rx,ry in resources:
            md=dist(sx,sy,rx,ry); od=dist(ox,oy,rx,ry)
            # Prefer resources where we are closer, otherwise contest by advantage gap
            key=(md-0.7*od, md, rx, ry)
            if best is None or key<best[0]: best=(key,(rx,ry))
        tx,ty=best[1]
    else:
        tx,ty=(w//2,h//2)
    moves=[(-1,-1),(-1,0),(-1,1),(0,-1),(0,0),(0,1),(1,-1),(1,0),(1,1)]
    best_move=(0,0); best_score=None
    for dx,dy in moves:
        nx,ny=sx+dx,sy+dy
        if not inb(nx,ny): 
            continue
        if (nx,ny) in obstacles:
            continue
        myd=dist(nx,ny,tx,ty)
        opd=dist(nx,ny,ox,oy)
        # If we're already on a resource, still keep pressure by moving away from opponent slightly
        on_res = (nx,ny) in set(resources) if resources else False
        score = -myd + (0.35*opd) + (-0.05 if on_res else 0.0) + (0.001*(dx*dx+dy*dy))
        if best_score is None or score>best_score:
            best_score=score; best_move=(dx,dy)
    return [int(best_move[0]), int(best_move[1])]