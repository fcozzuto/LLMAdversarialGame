def choose_move(observation):
    w = observation.get("grid_width") or 8
    h = observation.get("grid_height") or 8
    w = int(w)
    h = int(h)
    sp = observation.get("self_position") or (0, 0)
    sx, sy = int(sp[0]), int(sp[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    def ok(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    opp = observation.get("opponent_position") or (w - 1, h - 1)
    tx, ty = int(opp[0]), int(opp[1])

    moves = [(1, 0), (-1, 0), (0, 1), (0, -1), (0, 0)]
    best = (10**9, (0, 0))
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not ok(nx, ny):
            continue
        d = abs(nx - tx) + abs(ny - ty)
        if d < best[0]:
            best = (d, (dx, dy))
    return [best[1][0], best[1][1]]