def choose_move(observation):
    w, h = observation["grid_width"], observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources") or []
    obstacles = set((p[0], p[1]) for p in (observation.get("obstacles") or []))

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx >= dy else dy

    def legal(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    moves = [(-1,-1),(0,-1),(1,-1),(-1,0),(0,0),(1,0),(-1,1),(0,1),(1,1)]
    if not resources:
        tx, ty = w - 1 if sx < w//2 else 0, h - 1 if sy < h//2 else 0
        best = None
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not legal(nx, ny): 
                continue
            key = (cheb(ox, oy, tx, ty) - cheb(nx, ny, tx, ty), cheb(nx, ny, tx, ty), -nx, -ny, dx, dy)
            if best is None or key < best[0]:
                best = (key, [dx, dy])
        return best[1] if best else [0, 0]

    best = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not legal(nx, ny):
            continue
        # one-step lookahead: pick resource maximizing (opp_dist - our_dist) after our move
        best_key = None
        for rx, ry in resources:
            if (rx, ry) in obstacles:
                continue
            ds = cheb(nx, ny, rx, ry)
            do = cheb(ox, oy, rx, ry)
            # prioritize immediate collection, then margin, then tie-break deterministically
            key = (0 if ds == 0 else 1, -(do - ds), ds, -do, rx, ry)
            if best_key is None or key < best_key:
                best_key = key
        if best_key is None:
            continue
        # prefer moves that lead to better resource choice
        # add tiny preference to reduce distance to chosen resource and avoid oscillation via coords
        tie = (best_key[0], best_key[1], best_key[2], best_key[3], nx, ny, dx, dy)
        if best is None or tie < best[0]:
            best = (tie, [dx, dy])
    return best[1] if best else [0, 0]