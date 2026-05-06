def choose_move(observation):
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    w = int(observation.get("grid_width", 1))
    h = int(observation.get("grid_height", 1))
    resources = observation.get("resources") or []
    obstacles = observation.get("obstacles") or []
    obs = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obs.add((p[0], p[1]))
    def dist(a, b, c, d):
        dx = a - c
        if dx < 0: dx = -dx
        dy = b - d
        if dy < 0: dy = -dy
        return dx + dy
    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obs
    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    tx, ty = (w // 2, h // 2)
    if resources:
        best = None
        for r in resources:
            if isinstance(r, (list, tuple)) and len(r) >= 2:
                rx, ry = r[0], r[1]
                d = dist(sx, sy, rx, ry)
                if best is None or d < best[0]:
                    best = (d, rx, ry)
        if best is not None:
            tx, ty = best[1], best[2]
    best_score = None
    best_move = (0, 0)
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        d_self = dist(nx, ny, tx, ty)
        d_opp = dist(nx, ny, ox, oy)
        d_to_res = 0
        if resources:
            m = None
            for r in resources:
                if isinstance(r, (list, tuple)) and len(r) >= 2:
                    rx, ry = r[0], r[1]
                    d = dist(nx, ny, rx, ry)
                    if m is None or d < m:
                        m = d
            d_to_res = m if m is not None else d_self
        score = -d_to_res + 0.15 * d_opp
        if best_score is None or score > best_score:
            best_score = score
            best_move = (dx, dy)
        elif score == best_score:
            if (dx, dy) < best_move:
                best_move = (dx, dy)
    return [int(best_move[0]), int(best_move[1])]