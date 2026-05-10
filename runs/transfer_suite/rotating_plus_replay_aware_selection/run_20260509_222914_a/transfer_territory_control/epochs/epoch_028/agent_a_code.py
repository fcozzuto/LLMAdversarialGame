def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", (0, 0)) or (0, 0)
    ox, oy = observation.get("opponent_position", (sx, sy)) or (sx, sy)
    def inside(x, y): return 0 <= x < w and 0 <= y < h

    obs = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = p[0], p[1]
            if isinstance(x, int) and isinstance(y, int) and inside(x, y):
                obs.add((x, y))

    unclaimed = observation.get("unclaimed_cells") or observation.get("unclaimed") or []
    un = []
    for p in unclaimed:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = p[0], p[1]
            if isinstance(x, int) and isinstance(y, int) and inside(x, y) and (x, y) not in obs:
                un.append((x, y))
    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    best_mv = (0, 0)
    best_sc = -10**18
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inside(nx, ny) or (nx, ny) in obs:
            continue
        d_opp = abs(nx - ox) + abs(ny - oy)
        if un:
            d_un = 10**9
            for ux, uy in un:
                d = abs(nx - ux) + abs(ny - uy)
                if d < d_un: d_un = d
            sc = (-d_un * 10) + (d_opp)
        else:
            sc = (-abs(nx - (w - 1) // 2) - abs(ny - (h - 1) // 2)) + d_opp // 2
        if sc > best_sc:
            best_sc = sc
            best_mv = (dx, dy)

    if inside(sx, sy) and (sx, sy) not in obs:
        return [best_mv[0], best_mv[1]]
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if inside(nx, ny) and (nx, ny) not in obs:
            return [dx, dy]
    return [0, 0]