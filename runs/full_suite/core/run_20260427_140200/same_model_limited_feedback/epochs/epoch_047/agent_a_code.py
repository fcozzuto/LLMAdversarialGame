def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []

    def clamp(v, lo, hi):
        if v < lo:
            return lo
        if v > hi:
            return hi
        return v

    obs = set()
    for o in obstacles:
        try:
            ox0, oy0 = o
            obs.add((int(ox0), int(oy0)))
        except Exception:
            pass

    def d2(ax, ay, bx, by):
        dx = ax - bx
        dy = ay - by
        return dx * dx + dy * dy

    best_move = [0, 0]
    best_val = -10**18

    if resources:
        rx, ry = min(resources, key=lambda r: d2(int(r[0]), int(r[1]), ox, oy))
    else:
        rx, ry = sx, sy

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    for dx, dy in dirs:
        nx = clamp(sx + dx, 0, w - 1)
        ny = clamp(sy + dy, 0, h - 1)

        if (nx, ny) in obs:
            continue

        if (nx, ny) == (ox, oy):
            return [dx, dy]

        if resources:
            nr = min(resources, key=lambda r: d2(int(r[0]), int(r[1]), nx, ny))
            tx, ty = int(nr[0]), int(nr[1])
        else:
            tx, ty = rx, ry

        val = -d2(nx, ny, tx, ty)
        val += 0.35 * d2(nx, ny, ox, oy)
        val += 0.15 * (-d2(nx, ny, rx, ry))

        if val > best_val:
            best_val = val
            best_move = [dx, dy]

    return best_move