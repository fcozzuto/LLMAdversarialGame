def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    x, y = observation["self_position"]
    obstacles = set(tuple(p) for p in (observation.get("obstacles") or []))
    unclaimed = set(tuple(p) for p in (observation.get("unclaimed_cells") or []))
    selfT = set(tuple(p) for p in (observation.get("self_territory") or []))
    oppT = set(tuple(p) for p in (observation.get("opponent_territory") or []))
    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    if oppT:
        sx = sy = 0
        n = len(oppT)
        for px, py in oppT:
            sx += px
            sy += py
        ocx = sx / n
        ocy = sy / n
    else:
        ocx, ocy = w - 1, h - 1

    def inb(nx, ny):
        return 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles

    def unclaimed_neighbors(nx, ny):
        c = 0
        for ddx, ddy in dirs:
            ax, ay = nx + ddx, ny + ddy
            if 0 <= ax < w and 0 <= ay < h and (ax, ay) in unclaimed:
                c += 1
        return c

    best = -10**18
    best_move = [0, 0]
    for dx, dy in dirs:
        nx, ny = x + dx, y + dy
        if not inb(nx, ny):
            nx, ny = x, y
            dx, dy = 0, 0

        gain = 0.0
        if (nx, ny) in unclaimed:
            gain += 6.0 + 0.6 * unclaimed_neighbors(nx, ny)
        if (nx, ny) in oppT:
            gain += 4.5 + 0.25 * unclaimed_neighbors(nx, ny)
        if (nx, ny) in selfT:
            gain += 1.0

        d_op = abs(nx - ocx) + abs(ny - ocy)
        edge_pressure = (w + h - 2) - d_op
        score = gain + 0.07 * edge_pressure

        if score > best:
            best = score
            best_move = [dx, dy]

    return best_move