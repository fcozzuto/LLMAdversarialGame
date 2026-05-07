def choose_move(observation):
    w=observation["grid_width"]; h=observation["grid_height"]
    sx,sy=observation["self_position"]; ox,oy=observation["opponent_position"]
    resources=observation["resources"]; obstacles=set(tuple(p) for p in observation["obstacles"])
    def cheb(a,b,c,d):
        dx=abs(a-c); dy=abs(b-d)
        return dx if dx>dy else dy
    def inb(x,y):
        return 0<=x<w and 0<=y<h
    if not resources:
        return [0,0]
    best=None
    for rx,ry in resources:
        if (rx,ry) in obstacles:
            continue
        da=cheb(sx,sy,rx,ry)
        db=cheb(ox,oy,rx,ry)
        adv=(db-da)  # positive means we are closer
        score=adv*1000 - (da*10) - ((rx+ry)*0.001)
        if best is None or score>best[0]:
            best=(score,(rx,ry),da,db)
    if best is None:
        return [0,0]
    _,(tx,ty),_,_=best
    opp_to_target=cheb(ox,oy,tx,ty)
    deltas=[]
    for dx in (-1,0,1):
        for dy in (-1,0,1):
            deltas.append((dx,dy))
    cur_best=None; cur_move=(0,0)
    for dx,dy in deltas:
        nx=sx+dx; ny=sy+dy
        if not inb(nx,ny) or (nx,ny) in obstacles:
            continue
        our=cheb(nx,ny,tx,ty)
        adv=(opp_to_target-our)
        sc=adv*50 - our*2 - (dx*dx+dy*dy)*0.1
        if cur_best is None or sc>cur_best:
            cur_best=sc; cur_move=(dx,dy)
    return [int(cur_move[0]),int(cur_move[1])]