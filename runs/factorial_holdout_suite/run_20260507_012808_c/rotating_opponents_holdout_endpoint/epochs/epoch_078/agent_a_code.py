def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = set()
    for p in (observation.get("obstacles") or []):
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for r in (observation.get("resources") or []):
        if r and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def mindist(x, y, pts):
        if not pts:
            return 10**9
        best = 10**9
        for px, py in pts:
            d = abs(px - x) + abs(py - y)
            if d < best:
                best = d
        return best

    allowed = []
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles:
            allowed.append((dx, dy, nx, ny))

    if not allowed:
        return [0, 0]
    if not resources:
        bx = -10**9
        best = (0, 0)
        for dx, dy, nx, ny in allowed:
            d_opp = abs(nx - ox) + abs(ny - oy)
            sc = d_opp - (10**6 if (nx, ny) == (ox, oy) else 0)
            if sc > bx:
                bx, best = sc, (dx, dy)
        return [best[0], best[1]]

    best_sc = -10**18
    best_move = (0, 0)
    for dx, dy, nx, ny in allowed:
        if (nx, ny) == (ox, oy):
            sc = -10**12
        else:
            d_res = mindist(nx, ny, resources)
            d_opp = abs(nx - ox) + abs(ny - oy)
            sc = (d_opp * 2) - d_res
        if sc > best_sc:
            best_sc = sc
            best_move = (dx, dy)
    return [int(best_move[0]), int(best_move[1])]