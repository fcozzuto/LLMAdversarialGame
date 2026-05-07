def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [w - 1, h - 1])
    resources = observation.get("resources", []) or []
    obstacles_raw = observation.get("obstacles", []) or []

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    obs = set()
    for p in obstacles_raw:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = p[0], p[1]
            if isinstance(x, int) and isinstance(y, int) and inb(x, y):
                obs.add((x, y))

    if not (isinstance(sx, int) and isinstance(sy, int) and inb(sx, sy)):
        return [0, 0]
    if not (isinstance(ox, int) and isinstance(oy, int) and inb(ox, oy)):
        ox, oy = w - 1, h - 1

    rlist = []
    for r in resources:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = r[0], r[1]
            if isinstance(x, int) and isinstance(y, int) and inb(x, y) and (x, y) not in obs:
                rlist.append((x, y))
    if not rlist:
        return [0, 0]

    def dche(a, b, c, d):
        return max(abs(a - c), abs(b - d))

    opp_row = oy
    opp_col = ox

    def resource_score(x, y, psx, psy):
        ds = dche(psx, psy, x, y)
        do = dche(ox, oy, x, y)
        earlier = (do - ds)  # positive means we can reach earlier
        row_col_pen = 0
        if y == opp_row:
            row_col_pen += 2
        if x == opp_col:
            row_col_pen += 1
        # Prefer earlier wins strongly; break ties by being closer; avoid "even" races on opponent lines
        return (earlier * 10 - row_col_pen * 2, -ds, x, y)

    legal_moves = []
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            if inb(nx, ny) and (nx, ny) not in obs:
                legal_moves.append((dx, dy))
    if not legal_moves:
        return [0, 0]

    best_move = None
    best_val = None
    for dx, dy in legal_moves:
        nx, ny = sx + dx, sy + dy
        # Evaluate by best reachable resource from the next position
        v = None
        for (rx, ry) in rlist:
            sv = resource_score(rx, ry, nx, ny)
            v = sv if v is None or sv > v else v
        if v is None:
            continue
        if best_val is None or v > best_val:
            best_val = v
            best_move = (dx, dy)

    if best_move is None:
        return [0, 0]
    return [int(best_move[0]), int(best_move[1])]