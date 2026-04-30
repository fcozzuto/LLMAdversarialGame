def choose_move(observation):
    w=observation["grid_width"]; h=observation["grid_height"]
    sx,sy=observation["self_position"]; ox,oy=observation["opponent_position"]
    resources=observation.get("resources",[]); obstacles=set(map(tuple,observation.get("obstacles",[])))
    moves=[(dx,dy) for dx in (-1,0,1) for dy in (-1,0,1)]
    def inb(x,y): return 0<=x<w and 0<=y<h
    # pick best resource by "relative closeness" (prefer where we are much closer than opponent)
    best=None; bestv=-10**9
    for rx,ry in resources:
        dS=abs(rx-sx)+abs(ry-sy); dO=abs(rx-ox)+abs(ry-oy)
        v=(dO - dS)*100 - dS  # strong preference for resources opponent is less able to take
        if v>bestv:
            bestv=v; best=(rx,ry)
    if not best:
        tx,ty=(w//2,h//2)
    else:
        tx,ty=best
    # evaluate immediate move (with obstacle avoidance + opponent pressure)
    def score_pos(x,y):
        if (x,y) in obstacles: return -10**9
        s=0
        for rx,ry in resources:
            if x==rx and y==ry: s+=5000
        dS=abs(tx-x)+abs(ty-y)
        s+=2000 - 50*dS
        dO=abs(ox-x)+abs(oy-y)
        s+= -10*(8-dO)  # keep some distance from opponent
        # slight bias toward reducing distance to target more than opponent reduces theirs
        s+= (abs(tx-ox)+abs(ty-oy)) - (dS)
        return s
    bestm=(0,0); bests=-10**9
    for dx,dy in moves:
        nx,ny=sx+dx,sy+dy
        if not inb(nx,ny): continue
        # deterministically avoid stepping into obstacles even if engine would reject
        s=score_pos(nx,ny)
        if s>bests:
            bests=s; bestm=(dx,dy)
    # secondary fallback: deterministic step toward target avoiding obstacles
    if bests<=-10**8:
        for dx,dy in moves:
            nx,ny=sx+dx,sy+dy
            if inb(nx,ny) and (nx,ny) not in obstacles:
                if abs(tx-nx)+abs(ty-ny)<abs(tx-sx)+abs(ty-sy): return [dx,dy]
        return [0,0]
    return [bestm[0],bestm[1]]