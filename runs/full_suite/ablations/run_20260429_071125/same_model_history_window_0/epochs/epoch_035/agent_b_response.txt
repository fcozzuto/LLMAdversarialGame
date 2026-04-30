def choose_move(observation):
    w=observation["grid_width"]; h=observation["grid_height"]
    sx,sy=observation["self_position"]; ox,oy=observation["opponent_position"]
    resources=observation.get("resources",[]); obstacles=set(tuple(p) for p in observation.get("obstacles",[]))
    if not resources:
        dx=0; dy=0
        tx,ty=ox,oy
        # move toward center away from opponent
        cx,cy=(w-1)/2,(h-1)/2
        if sx<cx: dx+=1
        elif sx>cx: dx-=1
        if sy<cy: dy+=1
        elif sy>cy: dy-=1
        return [int(dx),int(dy)]
    def cheb(a,b,c,d):
        dx=a-c; dy=b-d
        if dx<0: dx=-dx
        if dy<0: dy=-dy
        return dx if dx>dy else dy
    moves=[(-1,-1),(-1,0),(-1,1),(0,-1),(0,0),(0,1),(1,-1),(1,0),(1,1)]
    best_move=(0,0); best_score=-10**18
    # precompute distances to resources for opponent current
    for dx,dy in moves:
        nx=sx+dx; ny=sy+dy
        if nx<0 or nx>=w or ny<0 or ny>=h: 
            continue
        if (nx,ny) in obstacles:
            score=-10**12
        else:
            # if landing on a resource, prioritize immediately
            on_res=0
            for rx,ry in resources:
                if nx==rx and ny==ry:
                    on_res=1; break
            if on_res:
                score=10**9
            else:
                # choose move that makes us comparatively closer to the best contested resource
                # score = max over resources of (opp_dist - self_dist) with slight preference to reduce self_dist
                cur=-10**18
                for rx,ry in resources:
                    ds=cheb(nx,ny,rx,ry)
                    do=cheb(ox,oy,rx,ry)
                    val=(do - ds)*100 - ds
                    if val>cur: cur=val
                # also keep a small preference for moving away from opponent if not contesting
                away=cheb(nx,ny,ox,oy)
                score=cur + away*0.5
        if score>best_score:
            best_score=score; best_move=(dx,dy)
    return [int(best_move[0]),int(best_move[1])]