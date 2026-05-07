def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    s = observation.get("self_position", [0, 0])
    o = observation.get("opponent_position", [0, 0])
    sx, sy = int(s[0]), int(s[1])
    ox, oy = int(o[0]), int(o[1])

    obstacles = observation.get("obstacles") or []
    blocked = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) == 2:
            blocked.add((int(p[0]), int(p[1])))

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in blocked

    def cd(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    if not valid(sx, sy):
        sx = 0 if sx < 0 else (w - 1 if sx >= w else sx)
        sy = 0 if sy < 0 else (h - 1 if sy >= h else sy)

    resources = observation.get("resources") or []
    res_points = []
    for r in resources:
        if isinstance(r, (list, tuple)) and len(r) == 2:
            rx, ry = int(r[0]), int(r[1])
            if valid(rx, ry):
                res_points.append((rx, ry))

    best_move = (0, 0)
    best_score = -10**18

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue

        if res_points:
            dmin = 10**9
            for rx, ry in res_points:
                d = cd(nx, ny, rx, ry)
                if d < dmin:
                    dmin = d
            score = -dmin
        else:
            cx, cy = (w - 1) // 2, (h - 1) // 2
            score = -cd(nx, ny, cx, cy)

        # Prefer moving away from opponent; avoid approaching if equally good.
        score -= 0.01 * cd(nx, ny, ox, oy)

        # Small deterministic tie-break: center then axes order by dx,dy.
        score += 1e-6 * (-(abs(nx - ox) + abs(ny - oy)))

        if score > best_score:
            best_score = score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]