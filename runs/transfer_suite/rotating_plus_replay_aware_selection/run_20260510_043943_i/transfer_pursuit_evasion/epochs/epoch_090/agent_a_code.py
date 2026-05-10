def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    role = str(observation.get("self_role", "")).lower()
    is_evader = ("evader" in role) or ("runner" in role) or ("escape" in role)

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def obstacle_pen(nx, ny):
        if (nx, ny) in obstacles:
            return 10**6
        # Small deterministic repulsion from nearby obstacles
        p = 0
        for ax, ay in obstacles:
            d = cheb(nx, ny, ax, ay)
            if d == 1: p += 3
            elif d == 2: p += 1
        return p

    best = None
    best_score = None
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h):
            continue
        if (nx, ny) in obstacles:
            continue

        d = cheb(nx, ny, ox, oy)
        pen = obstacle_pen(nx, ny)

        if is_evader:
            # Run away; slightly prefer edges/corners to exploit wall-run archetype.
            edge = (nx == 0 or nx == w - 1 or ny == 0 or ny == h - 1)
            corner = (nx in (0, w - 1) and ny in (0, h - 1))
            score = d * 10 - pen * 2 + (2 if edge else 0) + (6 if corner else 0)
        else:
            # Pursue; minimize distance, avoid obstacles strongly, prefer moves that improve both axes.
            score = -d * 10 - pen * 4
            # Extra tie-break toward aligned chase
            score += (1 if (nx - ox) == 0 or (ny - oy) == 0 else 0)

        if best_score is None or score > best_score:
            best_score = score
            best = [dx, dy]

    if best is None:
        return [0, 0]
    return best