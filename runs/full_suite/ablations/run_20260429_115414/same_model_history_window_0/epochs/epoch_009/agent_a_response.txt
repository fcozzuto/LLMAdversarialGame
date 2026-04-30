def choose_move(observation):
    x0, y0 = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w, h = observation["grid_width"], observation["grid_height"]
    obstacles = observation.get("obstacles", [])
    resources = observation.get("resources", [])
    obs_set = {(p[0], p[1]) for p in obstacles}
    move_order = [(0,0), (1,0), (-1,0), (0,1), (0,-1), (1,1), (1,-1), (-1,1), (-1,-1)]

    if not resources:
        # No visible resources: stay away from opponent while moving toward center-ish
        tx, ty = (w - 1) // 2, (h - 1) // 2
        best = None
        best_val = -10**18
        for dx, dy in move_order:
            nx, ny = x0 + dx, y0 + dy
            if nx < 0 or ny < 0 or nx >= w or ny >= h: 
                continue
            if (nx, ny) in obs_set:
                val = -10**12
            else:
                d1 = (nx - tx)*(nx - tx) + (ny - ty)*(ny - ty)
                d2 = (nx - ox)*(nx - ox) + (ny - oy)*(ny - oy)
                val = -d1 - 3.0 / (1 + d2)
            if val > best_val:
                best_val = val
                best = (dx, dy)
        return [best[0], best[1]] if best else [0,0]

    def dist2(a, b):
        return (a[0] - b[0])*(a[0] - b[0]) + (a[1] - b[1])*(a[1] - b[1])

    # Pick a target we can "beat" (resource where our distance advantage is best)
    selfp = (x0, y0)
    oppp = (ox, oy)
    best_res = None
    best_key = None
    for r in resources:
        rp = (r[0], r[1])
        d_self = dist2(selfp, rp)
        d_opp = dist2(oppp, rp)
        # Key: minimize our advantage gap; tie-break by being closer to it
        key = (d_self - d_opp, d_self, r[0], r[1])
        if best_key is None or key < best_key:
            best_key = key
            best_res = rp

    tx, ty = best_res
    best_move = (0,0)
    best_val = -10**18
    for dx, dy in move_order:
        nx, ny = x0 + dx, y0 + dy
        if nx < 0 or ny < 0 or nx >= w or ny >= h:
            continue
        if (nx, ny) in obs_set:
            val = -10**12
        else:
            d_to_t = (nx - tx)*(nx - tx) + (ny - ty)*(ny - ty)
            d_to_o = (nx - ox)*(nx - ox) + (ny - oy)*(ny - oy)
            # If too close to opponent, reduce value; also prefer keeping a slight distance.
            close_pen = 0.0
            if d_to_o <= 4:   # within 2 steps (squared dist <=4)
                close_pen = 5.0 + 2.0/(1+d_to_o)
            elif d_to_o <= 9: # within 3 steps
                close_pen = 1.5/(1+d_to_o)
            val = -d_to_t - close_pen
        if val > best_val:
            best_val = val
            best_move = (dx, dy)
    return [best_move[0], best_move[1]]