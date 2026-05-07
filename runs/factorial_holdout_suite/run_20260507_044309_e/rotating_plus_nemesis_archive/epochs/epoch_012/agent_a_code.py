def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    obstacles = observation.get("obstacles", []) or []
    blocked = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = p[0], p[1]
            if isinstance(x, int) and isinstance(y, int) and 0 <= x < w and 0 <= y < h:
                blocked.add((x, y))

    def inside(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in blocked

    resources = []
    for r in observation.get("resources", []) or []:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = r[0], r[1]
            if isinstance(x, int) and isinstance(y, int) and inside(x, y):
                resources.append((x, y))

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best = None
    best_score = -10**18

    has_resources = bool(resources)
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inside(nx, ny):
            continue
        res_term = 0
        if has_resources:
            dmin = 10**9
            for rx, ry in resources:
                d = abs(rx - nx) + abs(ry - ny)
                if d < dmin:
                    dmin = d
            res_term = -dmin
        opp_term = - (abs(ox - nx) + abs(oy - ny))
        center = - (abs((w - 1) / 2 - nx) + abs((h - 1) / 2 - ny)) * 0.01
        s = res_term * 10 + opp_term + center
        if best is None or s > best_score or (s == best_score and (dx, dy) < best):
            best_score = s
            best = (dx, dy)

    if best is not None:
        return [best[0], best[1]]
    return [0, 0]