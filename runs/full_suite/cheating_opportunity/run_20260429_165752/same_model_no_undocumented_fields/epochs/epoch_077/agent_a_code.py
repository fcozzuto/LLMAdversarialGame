def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    s = observation.get("self_position", [0, 0]) or [0, 0]
    o = observation.get("opponent_position", [0, 0]) or [0, 0]
    sx, sy = int(s[0]), int(s[1])
    ox, oy = int(o[0]), int(o[1])

    def inb(x, y): return 0 <= x < w and 0 <= y < h
    def sgn(v): return -1 if v < 0 else (1 if v > 0 else 0)
    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if inb(x, y):
                obstacles.add((x, y))

    resources = []
    for p in observation.get("resources") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if inb(x, y) and (x, y) not in obstacles:
                resources.append((x, y))

    cx, cy = (w - 1) // 2, (h - 1) // 2
    dirs = [(-1,-1),(0,-1),(1,-1),(-1,0),(0,0),(1,0),(-1,1),(0,1),(1,1)]

    target = (cx, cy)
    if resources:
        best, best_sc = target, -10**18
        for rx, ry in resources:
            ds = cheb(sx, sy, rx, ry)
            do = cheb(ox, oy, rx, ry)
            sc = (do - ds) * 10 - ds
            if do < ds:
                sc -= 30  # deprioritize races we're likely to lose
            if sc > best_sc:
                best_sc = sc
                best = (rx, ry)
        target = best

    tx, ty = target
    step = (sgn(tx - sx), sgn(ty - sy))
    candidates = []
    dx0, dy0 = step
    for dx, dy in dirs:
        if dx == dx0 and dy == dy0:
            candidates.append((dx, dy))
        else:
            candidates.append((dx, dy))

    # Try to move toward target; avoid obstacles.
    best_move, best_val = (0, 0), -10**18
    for dx, dy in candidates:
        nx, ny = sx + dx, sy + dy
        if inb(nx, ny) and (nx, ny) not in obstacles:
            val = -cheb(nx, ny, tx, ty)
            # If resources exist, slightly prefer moves that also block opponent.
            if resources:
                val += (cheb(nx, ny, ox, oy) == 0) * -100000
            if val > best_val:
                best_val = val
                best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]