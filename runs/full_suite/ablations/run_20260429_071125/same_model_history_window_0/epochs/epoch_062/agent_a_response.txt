def choose_move(observation):
    w=observation["grid_width"]; h=observation["grid_height"]
    sx,sy=observation["self_position"]; ox,oy=observation["opponent_position"]
    resources=observation["resources"]; obstacles=set((x,y) for x,y in observation["obstacles"])
    moves=[(dx,dy) for dx in (-1,0,1) for dy in (-1,0,1)]
    def inside(x,y): return 0<=x<w and 0<=y<h and (x,y) not in obstacles
    def dist2(a,b,c,d):
        dx=a-c; dy=b-d; return dx*dx+dy*dy
    if not resources:
        # No resources left: chase center if possible, else move away from opponent.
        cx,cy=(w-1)/2,(h-1)/2
        best=None; bestv=None
        for dx,dy in moves:
            nx,ny=sx+dx,sy+dy
            if not inside(nx,ny): continue
            v=(dist2(nx,ny,cx,cy), -dist2(nx,ny,ox,oy))
            if bestv is None or v<bestv: bestv=v; best=(dx,dy)
        return list(best if best is not None else (0,0))
    # Precompute opponent distance to each resource from current position.
    opp_d={tuple(r):dist2(ox,oy,r[0],r[1]) for r in resources}
    # Pick a target resource based on being closer (or next-best otherwise).
    best_target=None; best_td=None; best_oppen=10**18
    for r in resources:
        td=dist2(sx,sy,r[0],r[1]); od=opp_d[tuple(r)]
        # Prefer resources where we're closer; otherwise prefer minimizing opponent closeness.
        key=(0 if td<od else 1, td, od)
        if best_td is None or key<best_td:
            best_td=key; best_target=tuple(r); best_oppen=od
    tx,ty=best_target
    # If opponent is very close to the target, try to intercept/block by aiming for the midpoint direction.
    intercept=False
    if dist2(ox,oy,tx,ty) <= 2: intercept=True
    best_move=(0,0); best_score=None
    for dx,dy in moves:
        nx,ny=sx+dx,sy+dy
        if not inside(nx,ny): continue
        # Primary: move toward target
        my_to_target=dist2(nx,ny,tx,ty)
        # Secondary: if intercept, also reduce distance to opponent (to contest) or increase (to avoid) depending on who is closer.
        my_to_opp=dist2(nx,ny,ox,oy)
        opp_to_target=dist2(ox,oy,tx,ty)
        # Tertiary: avoid stepping into adjacent reach of opponent when not contesting
        opp_adj_block=0
        for r in resources:
            if dist2(ox,oy,r[0],r[1])<=1 and dist2(nx,ny,r[0],r[1])<=1:
                opp_adj_block=1
                break
        # Multi-resource fallback: compute best resource advantage after move.
        best_adv=-10**18
        for r in resources:
            r=tuple(r)
            myd=dist2(nx,ny,r[0],r[1]); od=opp_d[r]
            adv=(1 if myd<od else -1, -myd if myd<od else od)
            # keep scalar comparable
            sc=(100000 if myd<od else 0) + (-myd if myd<od else -od)
            if sc>best_adv: best_adv=sc
        score=(
            0 if not intercept else 1,
            my_to_target,
            0 if intercept and my_to_opp<opp_to_target else 1,
            opp_adj_block,
            -best_adv,
            my_to_opp
        )
        if best_score is None or score<best_score:
            best_score=score; best_move=(dx,dy)
    return [int(best_move[0]), int(best_move[1])]