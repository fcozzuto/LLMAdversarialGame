def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = p[0], p[1]
            if isinstance(x, int) and isinstance(y, int) and 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for p in observation.get("resources") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = p[0], p[1]
            if isinstance(x, int) and isinstance(y, int) and 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    if not resources:
        return [0, 0]

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h):
            continue
        if (nx, ny) in obstacles:
            continue

        # local 1-step lookahead: choose the resource we would most prefer next, while estimating opp pressure
        best_here = -10**18
        for rx, ry in resources:
            d_opp = cheb(ox, oy, rx, ry)
            d_us = cheb(nx, ny, rx, ry)
            on_resource = 1 if (nx == rx and ny == ry) else 0
            # Seek resources with high opponent distance (delay opp) even if slightly farther for us; but grab if reachable now.
            val = (2000 * on_resource) + (d_opp * 6) - (d_us * 3)
            # slight avoidance of stepping near obstacles
            if abs(nx - rx) + abs(ny - ry) <= 1 and obstacles:
                val -= 2
            if val > best_here:
                best_here = val

        # Prefer moves that don't let us be immediately trapped near obstacles
        trap_pen = 0
        for ex in (-1, 0, 1):
            for ey in (-1, 0, 1):
                cx, cy = nx + ex, ny + ey
                if 0 <= cx < w and 0 <= cy < h and (cx, cy) in obstacles:
                    trap_pen += 1
        score = best_here - trap_pen

        if best is None or score > best[0]:
            best = (score, dx, dy)

    if best is None:
        return [0, 0]
    return [int(best[1]), int(best[2])]