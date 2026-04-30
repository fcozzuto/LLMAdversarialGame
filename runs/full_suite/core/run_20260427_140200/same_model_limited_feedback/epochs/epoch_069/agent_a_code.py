def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", []) or []
    obstacles = set(tuple(p) for p in observation.get("obstacles", []) or [])

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def best_target():
        if not resources:
            return (w // 2, h // 2)
        best = resources[0]
        bx, by = best
        bd = (sx - bx) * (sx - bx) + (sy - by) * (sy - by)
        bo = (ox - bx) * (ox - bx) + (oy - by) * (oy - by)
        bv = bd + 0.2 * bo
        for r in resources[1:]:
            x, y = r
            ds = (sx - x) * (sx - x) + (sy - y) * (sy - y)
            do = (ox - x) * (ox - x) + (oy - y) * (oy - y)
            v = ds + 0.2 * do
            if v < bv:
                bv, best = v, r
        return tuple(best)

    tx, ty = best_target()
    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    best_m = (0, 0)
    best_s = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        ds = (nx - tx) * (nx - tx) + (ny - ty) * (ny - ty)
        od = (ox - tx) * (ox - tx) + (oy - ty) * (oy - ty)
        s = ds + (0 if resources else -(((nx - ox) * (nx - ox) + (ny - oy) * (ny - oy))))
        if resources:
            s += 0.05 * od
        if best_s is None or s < best_s:
            best_s, best_m = s, (dx, dy)
    dx, dy = best_m
    if not (-1 <= dx <= 1 and -1 <= dy <= 1):
        return [0, 0]
    return [int(dx), int(dy)]