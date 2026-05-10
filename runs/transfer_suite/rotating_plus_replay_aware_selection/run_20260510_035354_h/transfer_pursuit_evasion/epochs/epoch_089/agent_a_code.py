def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])
    obstacles = set()
    for p in observation.get("obstacles") or []:
        if p is not None and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))
    resources = observation.get("resources") or []
    remaining = observation.get("remaining_resource_count")
    if isinstance(remaining, (list, tuple)) and remaining:
        remaining = remaining[0]
    if remaining is None:
        remaining = len(resources) if isinstance(resources, list) else 0

    def sgn(a):
        return 0 if a == 0 else (1 if a > 0 else -1)

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def man(a, b, c, d):
        return abs(a - c) + abs(b - d)

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    if resources and remaining:
        best_target = None
        bd = 10**9
        for r in resources:
            if r is None:
                continue
            if isinstance(r, dict):
                x, y = r.get("x"), r.get("y")
            else:
                x, y = (r[0], r[1]) if len(r) >= 2 else (None, None)
            if x is None or y is None:
                continue
            x, y = int(x), int(y)
            if inb(x, y) and (x, y) not in obstacles:
                d = man(sx, sy, x, y)
                if d < bd:
                    bd = d
                    best_target = (x, y)
        target = best_target if best_target is not None else (ox, oy)
    else:
        target = (ox, oy)

    def obs_near(x, y):
        if not obstacles:
            return 0
        m = 10**9
        for ax, ay in obstacles:
            d = man(x, y, ax, ay)
            if d < m:
                m = d
                if m == 0:
                    break
        return m

    best = None
    bestv = -10**18
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue
        d_t = man(nx, ny, target[0], target[1])
        d_o = man(nx, ny, ox, oy)
        hn = obs_near(nx, ny)
        v = -d_t * 3 + d_o * 1 + hn * 0.7
        if dx == 0 and dy == 0:
            v -= 0.2
        if best is None or v > bestv or (v == bestv and (dx, dy) < best):
            bestv = v
            best = (dx, dy)
    return [best[0], best[1]] if best is not None else [sgn(ox - sx), sgn(oy - sy)]