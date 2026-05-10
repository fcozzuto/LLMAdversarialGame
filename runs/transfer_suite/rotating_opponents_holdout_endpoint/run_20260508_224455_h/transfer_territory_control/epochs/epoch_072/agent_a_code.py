def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0])
    sx, sy = int(sx), int(sy)

    obst = set()
    for c in observation.get("obstacles") or []:
        if isinstance(c, (list, tuple)) and len(c) >= 2:
            obst.add((int(c[0]), int(c[1])))

    def inside(x, y):
        return 0 <= x < w and 0 <= y < h

    def blocked(x, y):
        return (not inside(x, y)) or ((x, y) in obst)

    unclaimed = []
    for p in observation.get("unclaimed_cells") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            unclaimed.append((int(p[0]), int(p[1])))

    opp = set()
    for p in observation.get("opponent_territory") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            opp.add((int(p[0]), int(p[1])))

    opp_pos = observation.get("opponent_position")
    ox = oy = None
    if isinstance(opp_pos, (list, tuple)) and len(opp_pos) >= 2:
        ox, oy = int(opp_pos[0]), int(opp_pos[1])

    dirs = [(-1, 0), (1, 0), (0, -1), (0, 1)]
    if unclaimed:
        targets = unclaimed
    elif opp:
        targets = list(opp)
    elif ox is not None and oy is not None:
        targets = [(ox, oy)]
    else:
        targets = [(sx, sy)]

    def best_dist(x, y):
        bd = None
        for tx, ty in targets:
            d = abs(tx - x) + abs(ty - y)
            if bd is None or d < bd:
                bd = d
        return bd if bd is not None else 0

    best = None
    best_dxdy = (0, 0)
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if blocked(nx, ny):
            continue
        d = best_dist(nx, ny)
        score = -d
        if best is None or score > best:
            best = score
            best_dxdy = (dx, dy)

    if best is None:
        for dx, dy in [(0, 0)] + dirs:
            nx, ny = sx + dx, sy + dy
            if not blocked(nx, ny):
                return [dx, dy]
        return [0, 0]

    return [best_dxdy[0], best_dxdy[1]]