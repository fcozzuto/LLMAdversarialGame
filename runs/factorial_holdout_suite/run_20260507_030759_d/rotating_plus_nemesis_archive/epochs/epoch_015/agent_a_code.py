def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources") or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles") or []))
    moves = [(-1, -1), (-1, 0), (-1, 1),
             (0, -1), (0, 0), (0, 1),
             (1, -1), (1, 0), (1, 1)]
    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles
    def man(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)
    res = [(int(x), int(y)) for x, y in resources]
    if not res:
        return [0, 0]
    best = None
    best_val = -10**18
    for dx, dy in sorted(moves):
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        # Evaluate: pick the resource where we most outperform opponent next turn
        best_for_move = -10**18
        for tx, ty in res:
            if nx == tx and ny == ty:
                val = 10**12
            else:
                self_d = man(nx, ny, tx, ty)
                opp_best = 10**9
                for odx, ody in moves:
                    mx, my = ox + odx, oy + ody
                    if valid(mx, my):
                        d = man(mx, my, tx, ty)
                        if d < opp_best:
                            opp_best = d
                if opp_best == 10**9:
                    opp_best = man(ox, oy, tx, ty)
                # Primary: closeness advantage. Secondary: shorter self distance.
                val = (opp_best - self_d) * 1000 - self_d
            if val > best_for_move:
                best_for_move = val
        if best_for_move > best_val:
            best_val = best_for_move
            best = (dx, dy)
    if best is None:
        return [0, 0]
    return [int(best[0]), int(best[1])]