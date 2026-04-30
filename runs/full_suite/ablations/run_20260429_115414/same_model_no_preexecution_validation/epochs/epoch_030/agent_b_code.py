def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    obstacles = observation.get("obstacles", []) or []
    obs = set()
    for p in obstacles:
        if p is not None and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if inb(x, y):
                obs.add((x, y))

    resources = observation.get("resources", []) or []
    res = []
    for r in resources:
        if r is not None and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if inb(x, y) and (x, y) not in obs:
                res.append((x, y))

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def score_target(tx, ty):
        ds = cheb(sx, sy, tx, ty)
        do = cheb(ox, oy, tx, ty)
        # Prefer closer-and-faster relative to opponent, break ties by resource distance to your goal direction
        return (do - ds) * 100 - ds + (1 if ds == 0 else 0)

    if not res:
        # fallback: move to the farthest corner from opponent (while staying valid)
        corners = [(0, 0), (0, h - 1), (w - 1, 0), (w - 1, h - 1)]
        tx, ty = max(corners, key=lambda c: cheb(ox, oy, c[0], c[1]) - cheb(sx, sy, c[0], c[1]))
    else:
        tx, ty = max(res, key=lambda r: score_target(r[0], r[1]))

    best_move = (0, 0)
    best_val = -10**18
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obs:
            continue
        # Avoid letting opponent get closer; encourage moving toward target and away from opponent
        d_to_t = cheb(nx, ny, tx, ty)
        d_opp = cheb(nx, ny, ox, oy)
        d_opp_after = cheb(ox, oy, nx, ny)  # same as d_opp; kept for clarity
        # Mild preference for not oscillating by using turn_index parity to choose deterministic tie-break
        parity = observation.get("turn_index", 0) % 2
        val = -d_to_t * 10 + d_opp * 2 + (1 if d_to_t == 0 else 0) - ((dx + 1) + (dy + 1) + parity) * 1e-3
        if val > best_val:
            best_val = val
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]