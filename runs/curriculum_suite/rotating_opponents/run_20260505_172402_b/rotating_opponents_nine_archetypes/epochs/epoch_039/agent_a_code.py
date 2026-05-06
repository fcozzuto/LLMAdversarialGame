def choose_move(observation):
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))

    def in_bounds(x, y):
        return 0 <= x < w and 0 <= y < h

    obs_set = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if in_bounds(x, y):
                obs_set.add((x, y))

    resources = []
    for p in observation.get("resources") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if in_bounds(x, y) and (x, y) not in obs_set:
                resources.append((x, y))
    if not resources:
        return [0, 0]

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0:
            dx = -dx
        dy = ay - by
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    # Opportunistic target: where opponent can get it more easily than we can.
    best = None
    best_key = None
    for rx, ry in resources:
        sd = cheb(sx, sy, rx, ry)
        od = cheb(ox, oy, rx, ry)
        rel = od - sd
        key = (-rel, sd, rx, ry)
        if best is None or key < best_key:
            best = (rx, ry)
            best_key = key
    tx, ty = best

    # Local deterministic move evaluation with opponent pressure term.
    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    best_m = (0, 0)
    best_s = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not in_bounds(nx, ny) or (nx, ny) in obs_set:
            continue
        d_t = cheb(nx, ny, tx, ty)
        d_o = cheb(nx, ny, ox, oy)
        # Prefer reducing target distance while increasing distance from opponent.
        val = (-d_t) * 10 + d_o * 3 - (abs(nx - sx) + abs(ny - sy)) * 0.1
        # Deterministic tie-break: lexicographically smallest move that achieves best.
        key = (-val, dx, dy)
        if best_s is None or key < best_s:
            best_s = key
            best_m = (dx, dy)

    dx, dy = best_m
    return [int(dx), int(dy)]