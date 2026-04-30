def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    s = observation.get("self_position") or [0, 0]
    o = observation.get("opponent_position") or [0, 0]
    sx, sy = int(s[0]), int(s[1])
    ox, oy = int(o[0]), int(o[1])

    obstacles = set()
    for b in observation.get("obstacles") or []:
        if b and len(b) >= 2:
            bx, by = int(b[0]), int(b[1])
            if 0 <= bx < w and 0 <= by < h:
                obstacles.add((bx, by))

    resources = []
    for r in observation.get("resources") or []:
        if r and len(r) >= 2:
            rx, ry = int(r[0]), int(r[1])
            if 0 <= rx < w and 0 <= ry < h and (rx, ry) not in obstacles:
                resources.append((rx, ry))

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def dist2(x1, y1, x2, y2):
        dx = x1 - x2
        dy = y1 - y2
        return dx * dx + dy * dy

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    if resources:
        tx, ty = min(resources, key=lambda p: (cheb(sx, sy, p[0], p[1]), p[0], p[1]))
    else:
        tx = w - 1 if sx < w // 2 else 0
        ty = h - 1 if sy < h // 2 else 0

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    best_move = (0, 0)
    best_primary = None
    best_secondary = None

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        d_self = cheb(nx, ny, tx, ty)
        d_opp = cheb(ox, oy, tx, ty)
        # Prefer moves that get us closer to target; if opponent is closer, try to increase our separation.
        primary = d_self * 100 + (0 if cheb(nx, ny, ox, oy) > cheb(sx, sy, ox, oy) else 1)
        secondary = -dist2(nx, ny, ox, oy)
        # Also discourage stepping into a cell that makes it much easier for opponent to reach target next.
        opp_reach_if = cheb(nx, ny, ox, oy)  # deterministic slight shaping
        key_primary = primary + (1 if d_self > d_opp else 0) + (0 if opp_reach_if > 0 else 1)
        if best_primary is None or key_primary < best_primary or (key_primary == best_primary and secondary > best_secondary):
            best_primary = key_primary
            best_secondary = secondary
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]