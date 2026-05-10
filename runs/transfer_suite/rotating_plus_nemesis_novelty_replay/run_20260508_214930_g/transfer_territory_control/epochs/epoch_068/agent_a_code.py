def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    obstacles = set(tuple(p) for p in (observation.get("obstacles") or []))
    unclaimed = set(tuple(p) for p in (observation.get("unclaimed_cells") or []))

    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles
    def md(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    opp_t = set(tuple(p) for p in (observation.get("opponent_territory") or []))
    opp_adj = []
    if opp_t and unclaimed:
        for tx, ty in opp_t:
            for dx, dy in dirs:
                nx, ny = tx + dx, ty + dy
                if (nx, ny) in unclaimed:
                    opp_adj.append((nx, ny))
    targets = opp_adj if opp_adj else list(unclaimed)

    if not targets:
        best = (md(sx, sy, ox, oy), sx, sy)
        for dx, dy in dirs:
            nx, ny = sx + dx, sy + dy
            if not inb(nx, ny):
                continue
            d = md(nx, ny, ox, oy)
            cand = (d, nx, ny)
            if cand < best:
                best = cand
                bx, by = nx, ny
        return [bx - sx, by - sy]

    targets.sort(key=lambda t: (md(sx, sy, t[0], t[1]), t[0], t[1]))
    tx, ty = targets[0]

    best_move = (10**9, -10**9, sx, sy)
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        dist = md(nx, ny, tx, ty)
        gain = -(md(nx, ny, ox, oy))  # prefer moving closer to opponent if tied
        cand = (dist, gain, nx, ny)
        if cand < best_move:
            best_move = cand
            bx, by = nx, ny
    return [bx - sx, by - sy]