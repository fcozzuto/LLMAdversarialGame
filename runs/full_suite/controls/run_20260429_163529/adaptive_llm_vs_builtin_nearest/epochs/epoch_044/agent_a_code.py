def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position", [0, 0]) or [0, 0]
    op = observation.get("opponent_position", [w - 1, h - 1]) or [w - 1, h - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = observation.get("obstacles", []) or []
    obs = set()
    for p in obstacles:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obs.add((x, y))

    res = observation.get("resources", []) or []
    res_set = set()
    for p in res:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                res_set.add((x, y))

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    best = None
    best_score = -10**18

    # pick target: nearest resource if any, else keep away from opponent toward farther corner
    if res_set:
        tx, ty = min(res_set, key=lambda t: (cheb(sx, sy, t[0], t[1]), t[0], t[1]))
    else:
        # farther corner from opponent, deterministic tie-break
        corners = [(0, 0), (0, h - 1), (w - 1, 0), (w - 1, h - 1)]
        tx, ty = max(corners, key=lambda t: (cheb(t[0], t[1], ox, oy), -t[0], -t[1]))

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h):
            continue
        if (nx, ny) in obs:
            continue
        dres = cheb(nx, ny, tx, ty)
        dop = cheb(nx, ny, ox, oy)
        score = -dres * 10 + dop * 2
        if (nx, ny) in res_set:
            score += 10**6
            # discourage stepping into tight opponent range while grabbing
            score -= max(0, 3 - dop) * 50
        # slight preference for advancing toward target deterministically
        score -= (abs(nx - tx) + abs(ny - ty)) * 0.01
        if score > best_score:
            best_score = score
            best = [dx, dy]

    if best is None:
        # all moves blocked or out of bounds: stay put if possible, else pick any in-bounds non-obstacle
        if (sx, sy) not in obs:
            return [0, 0]
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obs:
                return [dx, dy]
        return [0, 0]
    return best