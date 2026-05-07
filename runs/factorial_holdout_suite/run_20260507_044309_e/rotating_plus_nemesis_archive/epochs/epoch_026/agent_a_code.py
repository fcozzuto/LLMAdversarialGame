def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    blocked = set()
    for p in (observation.get("obstacles", []) or []):
        try:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                blocked.add((x, y))
        except:
            pass

    resources = []
    for r in (observation.get("resources", []) or []):
        try:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in blocked:
                resources.append((x, y))
        except:
            pass
    if not resources:
        return [0, 0]

    def md(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    def cheb(a, b):
        dx = abs(a[0] - b[0])
        dy = abs(a[1] - b[1])
        return dx if dx > dy else dy

    best = None
    best_key = None
    for cell in resources:
        sd = cheb((sx, sy), cell)
        od = cheb((ox, oy), cell)
        gain = od - sd  # positive means we are closer
        tie = (cell[0] - sx) == 0 or (cell[1] - sy) == 0
        key = (gain, tie, -sd, -md((sx, sy), cell))
        if best_key is None or key > best_key:
            best_key = key
            best = cell

    tx, ty = best
    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    cur = (sx, sy)

    # Choose move that most reduces Chebyshev distance to target; break ties by opponent pressure.
    best_m = (0, 0)
    best_d = None
    best_press = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in blocked:
            d = cheb((nx, ny), (tx, ty))
            press = cheb((ox, oy), (tx, ty)) - d
            if best_d is None or (d < best_d) or (d == best_d and (press > best_press)):
                best_d = d
                best_press = press
                best_m = (dx, dy)

    if best_d is not None:
        return [int(best_m[0]), int(best_m[1])]

    # Fallback: allow blocked squares (engine may keep us in place).
    best_m = (0, 0)
    best_d = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if 0 <= nx < w and 0 <= ny < h:
            d = cheb((nx, ny), (tx, ty))
            if best_d is None or d < best_d:
                best_d = d
                best_m = (dx, dy)
    return [int(best_m[0]), int(best_m[1])]