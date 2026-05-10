def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx = int(sx); sy = int(sy); ox = int(ox); oy = int(oy)

    obstacles = set()
    for p in observation.get("obstacles", []) or []:
        if p and len(p) >= 2:
            x = int(p[0]); y = int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for r in observation.get("resources", []) or []:
        if r and len(r) >= 2:
            x = int(r[0]); y = int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    if not resources:
        return [0, 0]

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    # Deterministic target selection: maximize "reach before opponent", then finish sooner.
    best = None
    best_margin = None
    best_sd = None
    for rx, ry in resources:
        sd = cheb(sx, sy, rx, ry)
        od = cheb(ox, oy, rx, ry)
        margin = od - sd
        if best is None or margin > best_margin or (margin == best_margin and sd < best_sd):
            best = (rx, ry)
            best_margin = margin
            best_sd = sd

    rx, ry = best

    def sgn(a):
        return (a > 0) - (a < 0)

    desired_dx = sgn(rx - sx)
    desired_dy = sgn(ry - sy)

    moves = []
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx = sx + dx
            ny = sy + dy
            if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles:
                # Prefer moves that align with desired step; break ties by closeness to target.
                align = cheb(dx, dy, desired_dx, desired_dy)
                dist = cheb(nx, ny, rx, ry)
                moves.append((align, dist, dx, dy))
    if not moves:
        return [0, 0]

    moves.sort(key=lambda t: (t[0], t[1], t[2], t[3]))
    return [int(moves[0][2]), int(moves[0][3])]