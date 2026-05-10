def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []

    res = [(p[0], p[1]) for p in resources if p and len(p) >= 2]
    if not res:
        return [0, 0]
    obs = set((p[0], p[1]) for p in obstacles if p and len(p) >= 2)

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0:
            dx = -dx
        dy = y1 - y2
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    # Pick target resource with advantage for us (arrive sooner).
    best_main = None
    best_key = None
    center_x = (w - 1) / 2.0
    center_y = (h - 1) / 2.0

    safe = []
    for rx, ry in res:
        myd = cheb(sx, sy, rx, ry)
        opd = cheb(ox, oy, rx, ry)
        adv = opd - myd  # positive means we are closer
        # Prefer resources we can reach at least as fast as opponent
        if adv >= 0:
            safe.append((rx, ry, myd, opd, adv))
    cand = safe if safe else [(rx, ry, cheb(sx, sy, rx, ry), cheb(ox, oy, rx, ry), cheb(ox, oy, rx, ry) - cheb(sx, sy, rx, ry)) for rx, ry in res]

    for rx, ry, myd, opd, adv in cand:
        # Key: maximize advantage, then minimize our distance, then center tie-break (deterministic)
        cx = abs(rx - center_x)
        cy = abs(ry - center_y)
        key = (adv, -myd, -(cx + cy))
        if best_key is None or key > best_key:
            best_key = key
            best_main = (rx, ry, myd, opd)

    tx, ty, _, _ = best_main

    dirs = [(0, 0), (1, 0), (-1, 0), (0, 1), (0, -1), (1, 1), (1, -1), (-1, 1), (-1, -1)]
    # Choose best next step by evaluating our advantage after moving.
    best_move = [0, 0]
    best_score = None
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obs:
            continue
        # Evaluate against the chosen target first, then quick fallback to nearest resource advantage.
        myd_t = cheb(nx, ny, tx, ty)
        opd_t = cheb(ox, oy, tx, ty)
        adv_t = opd_t - myd_t
        # Small deterministic secondary: reduce distance to target
        score = (adv_t, -myd_t, -abs(nx - center_x) - abs(ny - center_y))
        if best_score is None or score > best_score:
            best_score = score
            best_move = [dx, dy]

    return best_move