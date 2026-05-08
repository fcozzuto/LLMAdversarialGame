def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])
    role = (observation.get("self_role") or "").lower()

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    def inb(x, y): return 0 <= x < w and 0 <= y < h
    def free(x, y): return inb(x, y) and (x, y) not in obstacles
    def cheb(x1, y1, x2, y2): return max(abs(x1 - x2), abs(y1 - y2))

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    pursuer = ("purs" in role) or ("hunter" in role) or ("chaser" in role)

    corners = [(0, 0), (w - 1, 0), (0, h - 1), (w - 1, h - 1)]
    best_dxdy = (0, 0)
    if pursuer:
        # Chase: minimize distance; if tied, prefer moves that reduce opponent cheb-distance and keep mobility.
        best = None  # (score, dx, dy)
        for dx, dy in dirs:
            nx, ny = sx + dx, sy + dy
            if not free(nx, ny): 
                continue
            d = cheb(nx, ny, ox, oy)
            # mobility count around (nx, ny)
            mob = 0
            for ex, ey in dirs:
                tx, ty = nx + ex, ny + ey
                if free(tx, ty): mob += 1
            # score: primary = -d, secondary = +mob, tertiary = -Manhattan to opponent (more direct)
            man = abs(nx - ox) + abs(ny - oy)
            score = (-d, mob, -man)
            if best is None or score > best[0]:
                best = (score, dx, dy)
                best_dxdy = (dx, dy)
        return [int(best_dxdy[0]), int(best_dxdy[1])]

    # Evader: maximize distance; if tied, drift toward farthest corner and keep mobility.
    # Choose farthest corner from opponent as a deterministic "escape" direction.
    far_corner = max(corners, key=lambda c: cheb(c[0], c[1], ox, oy))
    fx, fy = far_corner

    best = None  # (score, dx, dy)
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not free(nx, ny):
            continue
        d = cheb(nx, ny, ox, oy)
        mob = 0
        for ex, ey in dirs:
            tx, ty = nx + ex, ny + ey
            if free(tx, ty): mob += 1
        corner_dist = cheb(nx, ny, fx, fy)  # smaller is closer to escape corner
        # score: primary = +d, secondary = +mob, tertiary = -corner_dist
        score = (d, mob, -corner_dist)
        if best is None or score > best[0]:
            best = (score, dx, dy)
            best_dxdy = (dx, dy)
    return [int(best_dxdy[0]), int(best_dxdy[1])]