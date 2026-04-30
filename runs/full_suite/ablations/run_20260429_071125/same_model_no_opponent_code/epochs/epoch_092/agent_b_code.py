def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles", []) or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for p in observation.get("resources", []) or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    dirs = (-1, 0, 1)
    candidates = []
    for dx in dirs:
        for dy in dirs:
            nx, ny = sx + dx, sy + dy
            if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles:
                candidates.append((dx, dy, nx, ny))
    if not candidates:
        return [0, 0]

    cx, cy = (w - 1) // 2, (h - 1) // 2

    best = None
    for dx, dy, nx, ny in candidates:
        if resources:
            best_r = None
            for rx, ry in resources:
                ds = cheb(nx, ny, rx, ry)
                do = cheb(ox, oy, rx, ry)
                # Prefer closer to a resource, and prefer resources where we are not farther than opponent.
                key = (ds, max(0, ds - do), cheb(ox, oy, rx, ry), cheb(nx, ny, cx, cy), rx, ry)
                if best_r is None or key < best_r[0]:
                    best_r = (key, (rx, ry))
            score = best_r[0]
        else:
            # No resources visible: drift toward center to keep options open.
            score = (cheb(nx, ny, cx, cy), abs(nx - ox) + abs(ny - oy), nx, ny)
        if best is None or score < best:
            best = score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]