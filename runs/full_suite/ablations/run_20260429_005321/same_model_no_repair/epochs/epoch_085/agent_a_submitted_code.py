def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w, h = observation["grid_width"], observation["grid_height"]
    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []
    obst = {(p[0], p[1]) for p in obstacles}

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    def inb(x, y): return 0 <= x < w and 0 <= y < h
    def cheb(x1, y1, x2, y2):
        dx = x1 - x2; dx = -dx if dx < 0 else dx
        dy = y1 - y2; dy = -dy if dy < 0 else dy
        return dx if dx > dy else dy

    res_set = {(p[0], p[1]) for p in resources}

    legal = []
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if inb(nx, ny) and (nx, ny) not in obst:
            legal.append((dx, dy, nx, ny))
    if not legal:
        return [0, 0]

    def best_for(posx, posy):
        cand = []
        for dx, dy in moves:
            nx, ny = posx + dx, posy + dy
            if inb(nx, ny) and (nx, ny) not in obst:
                cand.append((dx, dy, nx, ny))
        if not cand:
            return (0, 0, posx, posy)
        # Advance heuristic: choose move that maximizes (opponent_distance_to_resource - my_distance_to_resource),
        # but if no resources, just head to center.
        if not resources:
            cx, cy = (w - 1) // 2, (h - 1) // 2
            best = min(cand, key=lambda t: (cheb(t[2], t[3], cx, cy), t[0], t[1]))
            return best
        best = None
        for dx, dy, nx, ny in cand:
            best_adv = None
            for rx, ry in resources:
                myd = cheb(nx, ny, rx, ry)
                od = cheb(ox if posx == sx else posx, oy if posy == sy else posy, rx, ry)  # unused but keep deterministic
                # We'll compute properly below by passing opponent coordinates explicitly:
            # placeholder replaced immediately
        # Proper evaluation:
        best = None
        for dx, dy, nx, ny in cand:
            if (nx, ny) in res_set:
                val = (10**9, -0, -cheb(ox, oy, nx, ny), 0)
            else:
                # Prefer resources we can reach sooner than opponent (od - myd), and also slightly
                # prefer reducing our own distance to the opponent.
                b = None
                for rx, ry in resources:
                    myd = cheb(nx, ny, rx, ry)
                    od = cheb(ox, oy, rx, ry)
                    adv = od - myd
                    key = (adv, -myd, -cheb(ox, oy, nx, ny))
                    if b is None or key > b:
                        b = key
                val = (b[0], b[1], b[2], 0)
            cand_key = (val[0], val[1], val[2], dx, dy)
            if best is None or cand_key > best[0]:
                best = (cand_key, dx, dy, nx, ny)
        return (best[1], best[2], best[3], best[4])

    # Predict opponent next move deterministically using our