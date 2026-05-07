def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []

    obs = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = p[0], p[1]
            if isinstance(x, int) and isinstance(y, int) and 0 <= x < w and 0 <= y < h:
                obs.add((x, y))

    def blocked(x, y):
        return (x, y) in obs or not (0 <= x < w and 0 <= y < h)

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0:
            dx = -dx
        dy = ay - by
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    if not resources:
        return [0, 0]

    best = None
    best_u = -10**18
    for r in resources:
        if not (isinstance(r, (list, tuple)) and len(r) >= 2):
            continue
        rx, ry = r[0], r[1]
        if not (isinstance(rx, int) and isinstance(ry, int)):
            continue
        if blocked(rx, ry):
            continue
        ds = cheb(sx, sy, rx, ry)
        do = cheb(ox, oy, rx, ry)
        u = (do - ds) * 60 - ds  # prefer resources we can take first
        if ds == 0:
            u += 10**6
        if u > best_u:
            best_u = u
            best = (rx, ry)

    if best is None:
        return [0, 0]

    rx, ry = best
    if sx == rx and sy == ry:
        return [0, 0]

    best_step = None
    best_d = 10**18
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            if blocked(nx, ny):
                continue
            d = cheb(nx, ny, rx, ry)
            # deterministic tie-break order: smaller dx then dy after d
            if d < best_d or (d == best_d and (best_step is None or (dx, dy) < best_step)):
                best_d = d
                best_step = (dx, dy)

    if best_step is None:
        return [0, 0]
    return [int(best_step[0]), int(best_step[1])]