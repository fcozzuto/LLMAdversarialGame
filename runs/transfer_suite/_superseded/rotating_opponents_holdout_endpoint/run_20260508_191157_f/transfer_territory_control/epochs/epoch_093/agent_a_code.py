def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sx, sy = observation.get("self_position") or [0, 0]
    ox, oy = observation.get("opponent_position") or [w - 1, h - 1]
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    cx, cy = (w - 1) // 2, (h - 1) // 2
    moves = [(-1, 0), (0, -1), (0, 0), (1, 0), (0, 1), (-1, -1), (-1, 1), (1, -1), (1, 1)]

    def score(nx, ny):
        d_opp = abs(nx - ox) + abs(ny - oy)
        d_ctr = abs(nx - cx) + abs(ny - cy)
        un = observation.get("unclaimed_cells") or []
        ut = None
        for c in un:
            if c and len(c) >= 2 and int(c[0]) == nx and int(c[1]) == ny:
                ut = 1
                break
        return (d_opp, ut or 0, -d_ctr)

    best = None
    best_sc = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h):
            continue
        if (nx, ny) in obstacles:
            continue
        sc = score(nx, ny)
        if best_sc is None or sc > best_sc:
            best_sc, best = sc, [dx, dy]
    if best is None:
        return [0, 0]
    return best