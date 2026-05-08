def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position", [0, 0]) or [0, 0]
    op = observation.get("opponent_position", [0, 0]) or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in (observation.get("obstacles") or []):
        if p is not None and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    def inside(x, y):
        return 0 <= x < w and 0 <= y < h

    resources = observation.get("resources")
    res_list = []
    if resources:
        for r in resources:
            if r is not None and len(r) >= 2:
                x, y = int(r[0]), int(r[1])
                if inside(x, y) and (x, y) not in obstacles:
                    res_list.append((x, y))
    if not res_list:
        res_list = [( (w - 1) // 2, (h - 1) // 2 )]

    cx, cy = (w - 1) / 2.0, (h - 1) / 2.0
    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    best = None
    best_score = -10**18

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inside(nx, ny) or (nx, ny) in obstacles:
            continue
        if (nx, ny) == (ox, oy):
            continue
        md = None
        for rx, ry in res_list:
            d = abs(nx - rx) + abs(ny - ry)
            if md is None or d < md:
                md = d
        score = -md
        score -= 0.2 * (abs(nx - cx) + abs(ny - cy))
        score += 0.01 * ((dx != 0) + (dy != 0))
        if score > best_score:
            best_score = score
            best = [dx, dy]

    if best is not None:
        return best
    for dx, dy in [(0, -1), (-1, 0), (1, 0), (0, 1), (0, 0)]:
        nx, ny = sx + dx, sy + dy
        if inside(nx, ny) and (nx, ny) not in obstacles and (nx, ny) != (ox, oy):
            return [dx, dy]
    return [0, 0]