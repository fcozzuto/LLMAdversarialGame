def choose_move(observation):
    w=observation["grid_width"]; h=observation["grid_height"]
    sx,sy=observation["self_position"]; ox,oy=observation["opponent_position"]
    resources=observation["resources"]; obstacles=set(tuple(p) for p in observation["obstacles"])
    # Choose a target resource based on race dynamics: prefer resources where we have relative advantage.
    if resources:
        best=None; best_key=None
        for rx,ry in resources:
            d_self=abs(rx-sx)+abs(ry-sy)
            d_opp=abs(rx-ox)+abs(ry-oy)
            # Greedy diagonal-friendly: use Chebyshev distance as well.
            d_self2=max(abs(rx-sx),abs(ry-sy))
            d_opp2=max(abs(rx-ox),abs(ry-oy))
            key=(d_self2 - 0.9*d_opp2, d_self2, rx, ry)
            if best_key is None or key<best_key:
                best_key=key; best=(rx,ry)
        tx,ty=best
    else:
        tx,ty=(w-1)//2,(h-1)//2

    deltas=[(dx,dy) for dx in (-1,0,1) for dy in (-1,0,1)]
    def inb(x,y): return 0<=x<w and 0<=y<h
    def dist_cheb(x1,y1,x2,y2): return max(abs(x2-x1),abs(y2-y1))
    def obstacle_pen(x,y):
        # Small penalty for proximity to obstacles to reduce getting stuck.
        pen=0
        for ax,ay in obstacles:
            dd=max(abs(ax-x),abs(ay-y))
            if dd==0: return 10
            if dd==1: pen+=2
            elif dd==2: pen+=1
        return pen

    best_move=(0,0); best_score=None
    for dx,dy in deltas:
        nx,ny=sx+dx,sy+dy
        if not inb(nx,ny): 
            continue
        if (nx,ny) in obstacles:
            continue
        # Avoid stepping onto opponent position if possible (deterministic safety).
        if (nx,ny)==(ox,oy):
            continue
        score=0.0
        if resources and (nx,ny) in set(tuple(r) for r in resources):
            score+=1000.0
        score-=dist_cheb(nx,ny,tx,ty)*3.0
        score-=obstacle_pen(nx,ny)*1.5
        # Keep relative race: prefer moves that improve our advantage over opponent.
        my_adv=dist_cheb(nx,ny,tx,ty)-dist_cheb(ox,oy,tx,ty)
        score-=my_adv*1.2
        # Slight preference for progress toward target rather than oscillation: tie-break with direct direction.
        score-=abs((tx-nx)) + abs((ty-ny)) * 0.01
        if best_score is None or score>best_score:
            best_score=score; best_move=(dx,dy)
    return [int(best_move[0]), int(best_move[1])]