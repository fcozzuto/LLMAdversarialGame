def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for r in observation.get("resources") or []:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    cx, cy = (w - 1) // 2, (h - 1) // 2

    def inside(x, y):
        return 0 <= x < w and 0 <= y < h

    def ok(x, y):
        return inside(x, y) and (x, y) not in obstacles

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0:
            dx = -dx
        dy = y1 - y2
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    best_move = (0, 0)
    best_val = -10**18

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not ok(nx, ny):
            continue

        # Value: nearest resource distance, encourage contesting only when advantageous,
        # avoid getting too close to opponent when it would help them, center as tie-break.
        if resources:
            myd = 10**9
            opd = 10**9
            for rx, ry in resources:
                d1 = cheb(nx, ny, rx, ry)
                if d1 < myd:
                    myd = d1
                d2 = cheb(ox, oy, rx, ry)
                if d2 < opd:
                    opd = d2
            # If we are closer than opponent, prioritize; if not, slightly discourage.
            val = -myd + 0.9 * (opd - myd)
        else:
            val = -cheb(nx, ny, cx, cy) - 0.1 * cheb(nx, ny, ox, oy)

        # Tactical spacing from opponent: avoid stepping into their immediate neighborhood.
        do = cheb(nx, ny, ox, oy)
        val -= 0.15 / (1 + do)

        # Slight bias toward center to prevent dithering.
        val -= 0.02 * cheb(nx, ny, cx, cy)

        if val > best_val:
            best_val = val
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]