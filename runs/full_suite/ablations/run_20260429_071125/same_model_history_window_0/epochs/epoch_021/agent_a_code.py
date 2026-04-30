def choose_move(observation):
    w=observation['grid_width']; h=observation['grid_height']
    sx,sy=observation['self_position']; ox,oy=observation['opponent_position']
    resources=observation['resources']; obstacles=set(map(tuple,observation['obstacles']))
    cand=[]
    for dx,dy in ((-1,-1),(-1,0),(-1,1),(0,-1),(0,0),(0,1),(1,-1),(1,0),(1,1)):
        nx=sx+dx; ny=sy+dy
        if not (0<=nx<w and 0<=ny<h) or (nx,ny) in obstacles: 
            continue
        cand.append((dx,dy,nx,ny))
    if not cand: 
        return [0,0]
    def md(x1,y1,x2,y2):
        return abs(x1-x2)+abs(y1-y2)
    # Evaluate move by best target resource with distance-advantage and simple opponent pressure
    best=None; bestv=-10**18
    for dx,dy,nx,ny in cand:
        v=0
        for rx,ry in resources:
            d_self=md(nx,ny,rx,ry)
            d_opp=md(ox,oy,rx,ry)
            # Prefer resources where we are closer; penalize where opponent is closer
            v+= (d_opp-d_self)*10 - d_self
            # Small bias to break ties toward nearer resources overall
            v-= md(ox,oy,nx,ny)*0.5
            # Avoid running into opponent when equally good
            if (abs(nx-ox)<=1 and abs(ny-oy)<=1): v-=50
        # Encourage movement when opponent already much closer to most resources: take a different heading
        v-= md(nx,ny,ox,oy)*0.2
        if best is None or v>bestv:
            bestv=v; best=[dx,dy]
    return [int(best[0]), int(best[1])]