def choose_move(observation):
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    obstacles = observation.get("obstacles") or []
    obs = set()
    for p in obstacles:
        try:
            x, y = int(p[0]), int(p[1])
            if inb(x, y):
                obs.add((x, y))
        except Exception:
            pass

    resources_raw = observation.get("resources") or []
    resources = []
    for p in resources_raw:
        try:
            x, y = int(p[0]), int(p[1])
            if inb(x, y) and (x, y) not in obs:
                resources.append((x, y))
        except Exception:
            pass

    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)
    moves = [(0, 0), (1, 0), (-1, 0), (0, 1), (0, -1), (1, 1), (1, -1), (-1, 1), (-1, -1)]

    legal = []
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if inb(nx, ny) and (nx, ny) not in obs:
            legal.append((dx, dy))
    if not legal:
        return [0, 0]

    def dist(ax, ay, bx, by):
        return abs(ax - bx) + abs(ay - by)

    # If resources exist, pick a target we can reach first (with a margin), otherwise head to the most "central" remaining resource.
    if resources:
        best_t = None
        best_score = None
        for tx, ty in resources:
            d_self = dist(sx, sy, tx, ty)
            d_opp = dist(ox, oy, tx, ty)
            # Prefer resources where we are closer; also prefer closer absolute distances as tiebreak.
            score = (d_self - d_opp, d_self + 0.1 * (tx + ty), tx * 0.01 + ty * 0.001)
            if best_score is None or score < best_score:
                best_score = score
                best_t = (tx, ty)
        tx, ty = best_t
    else:
        # No visible resources: move toward opponent-bias-free "nearest corner line" deterministically.
        corners = [(0, 0), (0, h - 1), (w - 1, 0), (w - 1, h - 1)]
        tx, ty = min(corners, key=lambda c: (dist(sx, sy, c[0], c[1]) + 0.1 * dist(ox, oy, c[0], c[1]), c[0] * 0.01 + c[1] * 0.001))

    # Choose move that minimizes our distance to chosen target, but penalize moves that let opponent get closer to it.
    best_m = (0, 0)
    best_mv = None
    for dx, dy in legal:
        nx, ny = sx + dx, sy + dy
        d_self = dist(nx, ny, tx, ty)
        d_opp = dist(ox, oy, tx, ty)
        # Approximate opponent pressure: if we step away (in terms of d_self) while opponent is already close, avoid.
        mv = (d_self, (d_self - d_opp), abs((nx + ny) - (tx + ty)) * 0.001, dx * 0.01 + dy * 0.001)
        if best_mv is None or mv < best_mv:
            best_mv = mv
            best_m = (dx, dy)

    return [int(best_m[0]), int(best_m[1])]