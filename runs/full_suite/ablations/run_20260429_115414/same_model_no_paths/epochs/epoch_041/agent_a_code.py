def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    s = observation.get("self_position", [0, 0]) or [0, 0]
    o = observation.get("opponent_position", [0, 0]) or [0, 0]
    sx, sy = int(s[0]), int(s[1])
    ox, oy = int(o[0]), int(o[1])

    obstacles = set()
    for b in (observation.get("obstacles") or []):
        if b and len(b) >= 2:
            bx, by = int(b[0]), int(b[1])
            if 0 <= bx < w and 0 <= by < h:
                obstacles.add((bx, by))

    resources = []
    for r in (observation.get("resources") or []):
        if r and len(r) >= 2:
            rx, ry = int(r[0]), int(r[1])
            if 0 <= rx < w and 0 <= ry < h and (rx, ry) not in obstacles:
                resources.append((rx, ry))

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def free(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    # Determine opponent corner for deterministic offense/contested path bias.
    opp_corner = (0, 0) if (ox <= 0 and oy <= 0) else (w - 1, h - 1) if (ox >= w - 1 and oy >= h - 1) else (w - 1 if ox < w // 2 else 0, h - 1 if oy < h // 2 else 0)

    best = None
    best_key = None
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not free(nx, ny):
            continue

        # Resource progress: minimize distance to nearest resource, tie-break by second-nearest.
        if resources:
            dlist = sorted(cheb(nx, ny, rx, ry) for (rx, ry) in resources)
            d1 = dlist[0]
            d2 = dlist[1] if len(dlist) > 1 else 99
        else:
            d1, d2 = 99, 99

        # Contest handling: avoid being too close to opponent while still advancing.
        do = cheb(nx, ny, ox, oy)
        opp_pen = 0
        if do == 0:
            opp_pen = 1000
        elif do == 1:
            opp_pen = 20
        elif do == 2:
            opp_pen = 6

        # Offense/trajectory bias: move toward opponent corner.
        toward = cheb(nx, ny, opp_corner[0], opp_corner[1])

        # Composite key (maximize): higher is better; we convert to a minimization key.
        # Prefer closer resources, then away from opponent, then toward opponent corner, deterministic tie by move.
        score_min_key = (d1, d2, opp_pen, toward, dx, dy)
        if best_key is None or score_min_key < best_key:
            best_key = score_min_key
            best = [dx, dy]

    if best is None:
        return [0, 0]
    return best