def choose_move(observation):
    W = observation["grid_width"]; H = observation["grid_height"]
    sx, sy = observation["self_position"]; ox, oy = observation["opponent_position"]
    resources = observation.get("resources") or []
    obstacles = observation.get("obstacles") or []
    obs = set((p[0], p[1]) for p in obstacles)
    res = set((p[0], p[1]) for p in resources)

    moves = [(-1,-1),(-1,0),(-1,1),(0,-1),(0,0),(0,1),(1,-1),(1,0),(1,1)]
    def inb(x,y): return 0 <= x < W and 0 <= y < H
    def legal(x,y): return inb(x,y) and (x,y) not in obs
    def clamp(x,y,dx,dy):
        nx, ny = x+dx, y+dy
        return (x,y) if not legal(nx,ny) else (nx,ny)
    def cheb(x1,y1,x2,y2):
        dx = x1-x2; dx = -dx if dx<0 else dx
        dy = y1-y2; dy = -dy if dy<0 else dy
        return dx if dx>dy else dy

    def best_resource_score(mx,my):
        if not resources: return -10**9
        best = -10**18
        for rx,ry in resources:
            if (rx,ry) in obs: 
                continue
            md = cheb(mx,my,rx,ry)
            od = cheb(ox,oy,rx,ry)
            # Favor resources I can reach not later than opponent.
            adv = od - md
            # Add small bias to closer resources and "easy take" this turn.
            take = 20 if (mx,my)==(rx,ry) else 0
            # Penalize if opponent is already strictly closer by more than 1.
            penalty = 10 if od < md-1 else 0
            score = 30*adv - 3*md + take - penalty
            if score > best: best = score
        return best

    # Immediate capture if possible.
    for dx,dy in moves:
        nx, ny = clamp(sx,sy,dx,dy)
        if (nx,ny) in res:
            return [dx,dy]

    # Prefer blocking opponent: move to reduce their best possible advantage next step.
    best_move = (0,0); best_val = -10**18
    for dx,dy in moves:
        mx,my = clamp(sx,sy,dx,dy)
        # Estimate my next-turn advantage.
        my_score = best_resource_score(mx,my)

        # Estimate opponent next positions (deterministic: assume they choose best for themselves).
        # We'll approximate by looking only at their immediate improvement with one step.
        opp_best = -10**18
        for odx,ody in moves:
            ax, ay = clamp(ox,oy,odx,ody)
            opp_best = max(opp_best, best_resource_score(ax,ay))
        # Net objective: maximize my score and minimize their score.
        val = my_score - 0.85*opp_best
        if val > best_val:
            best_val = val; best_move = (dx,dy)

    return [int(best_move[0]), int(best_move[1])]