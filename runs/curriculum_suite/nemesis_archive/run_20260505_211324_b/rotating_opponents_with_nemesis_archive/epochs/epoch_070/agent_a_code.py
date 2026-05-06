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

    def valid(nx, ny):
        return 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obs

    moves = []
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            if valid(nx, ny):
                moves.append((dx, dy, nx, ny))
    if not moves:
        return [0, 0]

    def md(ax, ay, bx, by):
        return abs(ax - bx) + abs(ay - by)

    if not resources:
        # fallback: drift toward board center while avoiding opponent
        cx, cy = (w - 1) // 2, (h - 1) // 2
        best = None
        for dx, dy, nx, ny in moves:
            score = md(nx, ny, cx, cy) - md(nx, ny, ox, oy)
            if best is None or score < best[0]:
                best = (score, dx, dy)
        return [best[1], best[2]]

    # Target: favor resources we can reach earlier; if behind everywhere, pick closest-to-equal race.
    best_t = None
    for rx, ry in resources:
        if (rx, ry) in obs:
            continue
        sd = md(sx, sy, rx, ry)
        od = md(ox, oy, rx, ry)
        desir = (od - sd)  # higher => we are closer than opponent
        if best_t is None or desir > best_t[0] or (desir == best_t[0] and sd < best_t[1]):
            best_t = (desir, sd, rx, ry)
    _, _, tx, ty = best_t

    # Move: minimize distance to target, but when behind, also push away from opponent (intercept/avoid easy steals).
    behind = md(sx, sy, tx, ty) - md(ox, oy, tx, ty) > 0
    w_t = 4 if not behind else 6
    w_o = -2 if not behind else -4  # negative means prefer larger opponent distance

    best = None
    for dx, dy, nx, ny in moves:
        d_t = md(nx, ny, tx, ty)
        d_o = md(nx, ny, ox, oy)
        score = w_t * d_t + w_o * d_o
        if best is None or score < best[0]:
            best = (score, dx, dy)
    return [best[1], best[2]]