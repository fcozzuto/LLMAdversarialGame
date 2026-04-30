def choose_move(observation):
    w=observation["grid_width"]; h=observation["grid_height"]
    sx,sy=observation["self_position"]; ox,oy=observation["opponent_position"]
    resources=observation.get("resources",[]); obstacles=set(tuple(p) for p in observation.get("obstacles",[]))
    moves=[(-1,-1),(-1,0),(-1,1),(0,-1),(0,0),(0,1),(1,-1),(1,0),(1,1)]
    def inb(x,y): return 0<=x<w and 0<=y<h
    # Pick best resource by advantage (self earlier than opponent), otherwise nearest
    best=None; bestv=-10**9
    for rx,ry in resources:
        ds=abs(rx-sx)+abs(ry-sy)
        do=abs(rx-ox)+abs(ry-oy)
        v=(do-ds)*10 - ds  # larger when opponent farther than us
        if best is None or v>bestv:
            bestv=v; best=(rx,ry)
    if best is None:
        # No resources: move away from opponent while staying safe
        tx,ty=ox,oy
    else:
        tx,ty=best
    # Evaluate candidate moves
    dxs=[-1,0,1]; dys=[-1,0,1]
    bestm=(0,0); bestmv=-10**9
    for dx in dxs:
        for dy in dys:
            nx,ny=sx+dx,sy+dy
            if not inb(nx,ny): continue
            if (nx,ny) in obstacles: continue
            # distance to target (Chebyshev via max of deltas to handle diagonals fairly)
            dtarget=max(abs(tx-nx),abs(ty-ny))
            # distance advantage over opponent after move
            d_opp=max(abs(tx-ox),abs(ty-oy))
            d_self=max(abs(tx-nx),abs(ty-ny))
            adv=(d_opp-d_self)*2
            # obstacle proximity penalty (discourage moving into cramped areas)
            pen=0
            for ax in (-1,0,1):
                for ay in (-1,0,1):
                    if ax==0 and ay==0: continue
                    px,py=nx+ax,ny+ay
                    if inb(px,py) and (px,py) in obstacles: pen+=1
            # Prefer staying off obstacles and generally reducing distance
            mv=adv*5 - dtarget - pen*0.5
            if mv>bestmv:
                bestmv=mv; bestm=(dx,dy)
    return [int(bestm[0]), int(bestm[1])]