def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obs = set()
    for p in observation.get("obstacles") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obs.add((x, y))

    resources = []
    for p in observation.get("resources") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obs:
                resources.append((x, y))
    if not resources:
        return [0, 0]

    def dist(a, b, c, d):
        t = a - c
        if t < 0:
            t = -t
        u = b - d
        if u < 0:
            u = -u
        return t + u

    best = None
    best_val = None
    for tx, ty in resources:
        d1 = dist(sx, sy, tx, ty)
        d2 = dist(ox, oy, tx, ty)
        val = d1 - 0.35 * d2
        if best_val is None or val < best_val or (val == best_val and (tx, ty) < best):
            best_val = val
            best = (tx, ty)

    tx, ty = best
    moves = [(0, 0), (1, 0), (-1, 0), (0, 1), (0, -1)]
    best_step = (0, 0)
    best_d = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h):
            continue
        if (nx, ny) in obs:
            continue
        d = dist(nx, ny, tx, ty)
        if best_d is None or d < best_d or (d == best_d and (dx, dy) < best_step):
            best_d = d
            best_step = (dx, dy)

    dx, dy = best_step
    return [int(dx), int(dy)]