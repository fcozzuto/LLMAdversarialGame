def choose_move(observation):
    w=observation["grid_width"]; h=observation["grid_height"]
    sx,sy=observation["self_position"]; ox,oy=observation["opponent_position"]
    resources=observation["resources"]; obstacles=set(tuple(p) for p in observation["obstacles"])
    obs=set(obstacles)
    def clamp(x,a,b): return a if x<a else b if x>b else x
    moves=[(-1,-1),(-1,0),(-1,1),(0,-1),(0,0),(0,1),(1,-1),(1,0),(1,1)]
    def inb(x,y): return 0<=x<w and 0<=y<h
    def dist(a,b,c,d): return abs(a-c)+abs(b-d)
    bestR=None; bestScore=-10**9
    for rx,ry in resources:
        myd=dist(sx,sy,rx,ry); opd=dist(ox,oy,rx,ry)
        score=(opd-myd) * 100 - myd  # prioritize resources opponent can't reach first
        if score>bestScore or (score==bestScore and (bestR is None or (myd,rx,ry)<(dist(sx,sy,bestR[0],bestR[1]),bestR[0],bestR[1]))):
            bestScore=score; bestR=(rx,ry)
    if bestR is None:
        tx,ty=clamp((sx+ox)//2,0,w-1), clamp((sy+oy)//2,0,h-1)
    else:
        tx,ty=bestR
    bestMove=(0,0); bestVal=-10**9
    for dx,dy in moves:
        nx,ny=sx+dx,sy+dy
        if not inb(nx,ny) or (nx,ny) in obs: continue
        myd=dist(nx,ny,tx,ty)
        # if target scarce, also avoid letting opponent get closer
        opd=dist(ox,oy,tx,ty)
        val=(opd-myd)*100 - myd
        # slight bias away from obstacles (prefer open neighbors)
        neigh=0
        for ex,ey in moves:
            ax,ay=nx+ex,ny+ey
            if inb(ax,ay) and (ax,ay) not in obs: neigh+=1
        val+=neigh*0.5
        if val>bestVal:
            bestVal=val; bestMove=(dx,dy)
    dx,dy=bestMove
    if not inb(sx+dx,sy+dy) or (sx+dx,sy+dy) in obs: return [0,0]
    return [int(dx),int(dy)]