def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obs = set()
    for p in (observation.get("obstacles") or []):
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obs.add((x, y))

    resources = observation.get("resources") or []
    deltas = [(-1, 0), (1, 0), (0, -1), (0, 1), (0, 0), (-1, -1), (-1, 1), (1, -1), (1, 1)]

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obs

    def man(ax, ay, bx, by):
        return abs(ax - bx) + abs(ay - by)

    if resources:
        best_t = None
        best_d = 10**9
        for r in resources:
            if isinstance(r, (list, tuple)) and len(r) >= 2:
                tx, ty = int(r[0]), int(r[1])
                if 0 <= tx < w and 0 <= ty < h and (tx, ty) not in obs:
                    d = man(sx, sy, tx, ty)
                    if d < best_d:
                        best_d, best_t = d, (tx, ty)
        tx, ty = best_t if best_t is not None else (ox, oy)
    else:
        tx, ty = ox, oy

    best_move = None
    best_score = -10**18
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        d_t = man(nx, ny, tx, ty)
        d_o = man(nx, ny, ox, oy)
        score = -d_t + (2 if resources else 0) * (d_o) - (1 if (nx, ny) == (ox, oy) else 0)
        if best_move is None or score > best_score:
            best_score = score
            best_move = [dx, dy]
    if best_move is None:
        return [0, 0]
    return best_move