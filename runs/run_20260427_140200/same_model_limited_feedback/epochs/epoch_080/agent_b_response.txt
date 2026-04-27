def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation["resources"]
    obstacles = set((p[0], p[1]) for p in observation["obstacles"])
    dirs = [(-1,-1),(0,-1),(1,-1),(-1,0),(0,0),(1,0),(-1,1),(0,1),(1,1)]
    def inb(x,y): return 0 <= x < w and 0 <= y < h
    def dist(a,b,c,d):
        dx = abs(a-c); dy = abs(b-d)
        return dx if dx > dy else dy  # chebyshev
    def best_target():
        if not resources:
            return (sx, sy)
        best = None
        best_adv = -10**9
        best_ds = 10**9
        for rx, ry in resources:
            if (rx, ry) in obstacles: 
                continue
            ds = dist(sx, sy, rx, ry)
            do = dist(ox, oy, rx, ry)
            adv = do - ds  # positive: we're closer
            if adv > best_adv or (adv == best_adv and ds < best_ds):
                best_adv, best_ds, best = adv, ds, (rx, ry)
        return best if best is not None else (sx, sy)
    tx, ty = best_target()
    best_move = (0, 0)
    best_score = -10**18
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue
        d_to_t = dist(nx, ny, tx, ty)
        d_to_o = dist(nx, ny, ox, oy)
        # Prefer getting closer to our target; discourage walking into opponent range; slight tie-break to avoid obstacles near us
        step_cost = d_to_t * 10 - d_to_o
        # If we're already on target, stay put
        if (sx, sy) == (tx, ty):
            cand_score = 100000 - (dx*0 + dy*0)
        else:
            # Bonus for closing advantage against opponent at the target
            d_s_now = dist(sx, sy, tx, ty)
            d_o_now = dist(ox, oy, tx, ty)
            adv_now = d_o_now - d_s_now
            d_s_next = d_to_t
            adv_next = d_o_now - d_s_next
            cand_score = -step_cost + (adv_next - adv_now) * 20
        if cand_score > best_score:
            best_score = cand_score
            best_move = (dx, dy)
    return [int(best_move[0]), int(best_move[1])]