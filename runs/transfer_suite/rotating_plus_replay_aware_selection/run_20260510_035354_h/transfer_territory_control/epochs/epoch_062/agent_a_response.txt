def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    ax, ay = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    obstacles = observation.get("obstacles") or []
    oset = {(p[0], p[1]) for p in obstacles if isinstance(p, (list, tuple)) and len(p) >= 2}
    unclaimed = observation.get("unclaimed_cells") or []
    uset = {(p[0], p[1]) for p in unclaimed if isinstance(p, (list, tuple)) and len(p) >= 2}
    opp_terr = observation.get("opponent_territory") or []
    opset = {(p[0], p[1]) for p in opp_terr if isinstance(p, (list, tuple)) and len(p) >= 2}
    self_terr = observation.get("self_territory") or []
    sset = {(p[0], p[1]) for p in self_terr if isinstance(p, (list, tuple)) and len(p) >= 2}

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def man(x1, y1, x2, y2):
        d1 = x1 - x2
        if d1 < 0: d1 = -d1
        d2 = y1 - y2
        if d2 < 0: d2 = -d2
        return d1 + d2

    cx, cy = (w - 1) / 2.0, (h - 1) / 2.0
    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    best = (0, 0)
    best_sc = -10**18
    for dx, dy in moves:
        nx, ny = ax + dx, ay + dy
        if not inb(nx, ny) or (nx, ny) in oset:
            continue
        d_opp = man(nx, ny, ox, oy)
        dc = abs(nx - cx) + abs(ny - cy)
        if (nx, ny) in uset:
            sc = 120 - 3.0 * dc - 1.2 * d_opp
        elif (nx, ny) in opset:
            sc = 220 - 2.0 * dc - 2.0 * d_opp
        elif (nx, ny) in sset:
            sc = 20 - 1.5 * dc - 0.5 * d_opp
        else:
            sc = 5 - 1.2 * dc - 0.6 * d_opp
        if sc > best_sc:
            best_sc = sc
            best = (dx, dy)
    return [best[0], best[1]]