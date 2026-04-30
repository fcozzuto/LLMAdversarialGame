def choose_move(observation):
    w=observation["grid_width"]; h=observation["grid_height"]
    sx,sy=observation["self_position"]; ox,oy=observation["opponent_position"]
    resources=observation["resources"]; obstacles=set(tuple(p) for p in observation["obstacles"])
    moves=[(dx,dy) for dx in (-1,0,1) for dy in (-1,0,1)]
    # pick target resource: prefer ones where we're relatively closer than opponent
    if not resources:
        # fallback: move toward center while keeping away from opponent
        tx,ty=(w-1)/2,(h-1)/2
        best=None
        for dx,dy in moves:
            nx,ny=sx+dx,sy+dy
            if nx<0 or ny<0 or nx>=w or ny>=h or (nx,ny) in obstacles: 
                continue
            v=-(nx-tx)*(nx-tx)-(ny-ty)*(ny-ty) + 0.02*((nx-ox)*(nx-ox)+(ny-oy)*(ny-oy))
            if best is None or v>best[0]: best=(v,dx,dy)
        if best: return [best[1],best[2]]
        return [0,0]
    def dist2(a,b,c,d): 
        return (a-c)*(a-c)+(b-d)*(b-d)
    opp_dists=[dist2(p[0],p[1],ox,oy) for p in resources]
    self_dists=[dist2(p[0],p[1],sx,sy) for p in resources]
    best_t=None
    for i,p in enumerate(resources):
        sd=self_dists[i]; od=opp_dists[i]
        # relative advantage: smaller (sd-od) is better; tie-break prefer closer to us, then away from opponent
        key=(sd-od, sd, -od, p[0], p[1])
        if best_t is None or key<best_t[0]: best_t=(key,p)
    tx,ty=best_t[1]
    best_score=None; best_move=(0,0)
    for dx,dy in moves:
        nx,ny=sx+dx,sy+dy
        if nx<0 or ny<0 or nx>=w or ny>=h or (nx,ny) in obstacles: 
            continue
        dself=dist2(nx,ny,tx,ty)
        dobb=dist2(nx,ny,ox,oy)
        # also slightly prefer not oscillating: prefer moves that reduce our distance to target
        cur=dist2(sx,sy,tx,ty)
        score=-(dself) + 0.03*dobb + 0.001*(cur-dself)
        # if landing on a resource, prioritize strongly
        if (nx,ny) in set(tuple(r) for r in resources): score+=1e6
        if best_score is None or score>best_score:
            best_score=score; best_move=(dx,dy)
    return [best_move[0],best_move[1]]