def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obstacles.add((int(p[0]), int(p[1])))

    role_self = (observation.get("self_role") or "").lower()
    is_evader = ("evader" in role_self) or ("pursuer" not in role_self and "hunter" not in role_self and "chaser" not in role_self)

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def dist2(ax, ay, bx, by):
        dx, dy = ax - bx, ay - by
        return dx * dx + dy * dy

    if is_evader:
        corners = [(0, 0), (0, h - 1), (w - 1, 0), (w - 1, h - 1)]
        best_corner = max(corners, key=lambda c: dist2(c[0], c[1], ox, oy))
        tx, ty = best_corner
        best = None
        best_key = None
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not valid(nx, ny):
                continue
            d_foe = dist2(nx, ny, ox, oy)
            d_corner = -dist2(nx, ny, tx, ty)
            key = (d_foe, d_corner, -abs(dx), -abs(dy), nx, ny)
            if best_key is None or key > best_key:
                best_key = key
                best = (dx, dy)
        if best is None:
            return [0, 0]
        return [best[0], best[1]]

    best = None
    best_key = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        d = dist2(nx, ny, ox, oy)
        tie = (abs(dx) + abs(dy), nx, ny)
        key = (-d, -tie[0], -tie[1], -tie[2], dx, dy)
        if best_key is None or key > best_key:
            best_key = key
            best = (dx, dy)
    if best is None:
        return [0, 0]
    return [best[0], best[1]]