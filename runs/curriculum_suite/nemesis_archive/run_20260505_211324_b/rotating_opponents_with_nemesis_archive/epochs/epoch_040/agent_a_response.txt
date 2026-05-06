def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    resources = observation.get("resources") or []
    obstacles = observation.get("obstacles") or []

    obs = set()
    for o in obstacles:
        if isinstance(o, (list, tuple)) and len(o) == 2:
            x, y = o[0], o[1]
            if isinstance(x, int) and isinstance(y, int) and 0 <= x < w and 0 <= y < h:
                obs.add((x, y))

    res = []
    for r in resources:
        if isinstance(r, (list, tuple)) and len(r) == 2:
            x, y = r[0], r[1]
            if isinstance(x, int) and isinstance(y, int) and 0 <= x < w and 0 <= y < h and (x, y) not in obs:
                res.append((x, y))
    if not res:
        return [0, 0]

    def md(ax, ay, bx, by):
        return abs(ax - bx) + abs(ay - by)

    moves = [(dx, dy) for dx in (-1, 0, 1) for dy in (-1, 0, 1)]
    valid_moves = []
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obs:
            valid_moves.append((dx, dy))
    if not valid_moves:
        valid_moves = [(0, 0)]

    best_move = (0, 0)
    best_val = -10**18

    for dx, dy in valid_moves:
        nx, ny = sx + dx, sy + dy
        move_best = -10**18
        for tx, ty in res:
            self_d = md(nx, ny, tx, ty)
            # Greedy 1-step opponent toward this same target (approximate response)
            opp_next_d = 10**9
            for odx, ody in moves:
                mx, my = ox + odx, oy + ody
                if 0 <= mx < w and 0 <= my < h and (mx, my) not in obs:
                    d = md(mx, my, tx, ty)
                    if d < opp_next_d:
                        opp_next_d = d
            val = (opp_next_d - self_d) * 6 - self_d
            # Slightly prefer resources that aren't "behind" opponent relative to self
            val += (1 if md(ox, oy, tx, ty) >= md(sx, sy, tx, ty) else 0) * 1
            if val > move_best:
                move_best = val
        if move_best > best_val or (move_best == best_val and (dx, dy) < best_move):
            best_val = move_best
            best_move = (dx, dy)

    return [best_move[0], best_move[1]]