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

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obs

    moves = []
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            if inb(nx, ny):
                moves.append((dx, dy, nx, ny))
    if not moves:
        return [0, 0]

    def md(ax, ay, bx, by):
        return abs(ax - bx) + abs(ay - by)

    if not resources:
        best = min(moves, key=lambda t: (md(t[2], t[3], ox, oy), t[0], t[1]))
        return [int(best[0]), int(best[1])]

    res = []
    for r in resources:
        if isinstance(r, (list, tuple)) and len(r) == 2:
            x, y = r[0], r[1]
            if isinstance(x, int) and isinstance(y, int) and 0 <= x < w and 0 <= y < h and (x, y) not in obs:
                res.append((x, y))
    if not res:
        return [0, 0]

    best_move = None
    best_key = None
    for dx, dy, nx, ny in moves:
        # Prefer grabbing resources where we have a deterministic distance advantage over opponent
        best_val = -10**9
        worst_pen = 0
        for rx, ry in res:
            d_me = md(nx, ny, rx, ry)
            d_opp = md(ox, oy, rx, ry)
            adv = d_opp - d_me
            # If we can reach before (or sooner), strongly prefer; otherwise mildly discourage
            val = adv * 12 - d_me
            if adv >= 0:
                val += 25
            else:
                val -= 8
            if val > best_val:
                best_val = val
        # Secondary: keep moving in a useful direction vs opponent sweep
        # (bias to reduce our distance to the "frontier" row/col toward opponent)
        frontier = (ox, oy)
        worst_pen = md(nx, ny, frontier[0], frontier[1])
        key = (-best_val, worst_pen, dx, dy)
        if best_key is None or key < best_key:
            best_key = key
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]