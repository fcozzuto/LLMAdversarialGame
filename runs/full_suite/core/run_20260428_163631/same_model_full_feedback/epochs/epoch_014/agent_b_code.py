def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = set()
    for p in observation.get("obstacles", []) or []:
        if isinstance(p, (list, tuple)) and len(p) == 2:
            obstacles.add((int(p[0]), int(p[1])))

    resources = []
    for p in observation.get("resources", []) or []:
        if isinstance(p, (list, tuple)) and len(p) == 2:
            x, y = int(p[0]), int(p[1])
            if (x, y) not in obstacles:
                resources.append((x, y))

    def inb(x, y): return 0 <= x < w and 0 <= y < h
    def safe(x, y): return inb(x, y) and (x, y) not in obstacles
    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    dirs = [(0, 0), (1, 0), (-1, 0), (0, 1), (0, -1), (1, 1), (1, -1), (-1, 1), (-1, -1)]
    best_move, best_val = (0, 0), -10**18

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not safe(nx, ny):
            continue

        do = cheb(nx, ny, ox, oy)
        base = do * 0.15  # slight preference to stay away

        if not resources:
            val = base
        else:
            val = -10**9
            for rx, ry in resources:
                myd = cheb(nx, ny, rx, ry)
                opd = cheb(ox, oy, rx, ry)
                # Prefer resources where we are (or can become) closer than opponent
                contest = (opd - myd)
                # Stronger when we're near; slight preference for nearer overall
                score = contest * 2.0 - myd * 0.8
                # If very close to the resource, boost
                if myd == 0:
                    score += 50.0
                val = max(val, score)
            val += base

        if val > best_val:
            best_val, best_move = val, (dx, dy)
        elif val == best_val:
            # Deterministic tie-break: prefer smaller dx, then smaller dy
            if (dx, dy) < best_move:
                best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]