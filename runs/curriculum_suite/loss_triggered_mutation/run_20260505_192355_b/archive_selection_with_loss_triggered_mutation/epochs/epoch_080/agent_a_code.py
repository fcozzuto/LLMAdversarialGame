def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = observation.get("obstacles", []) or []
    obst = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obst.add((x, y))

    resources = observation.get("resources", []) or []
    res = []
    for r in resources:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obst:
                res.append((x, y))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obst

    moves = [(-1,-1),(0,-1),(1,-1),(-1,0),(0,0),(1,0),(-1,1),(0,1),(1,1)]

    if not inb(sx, sy):
        for dx, dy in moves:
            if inb(sx + dx, sy + dy):
                return [dx, dy]
        return [0, 0]

    if not res:
        # move toward center to avoid stagnation
        cx, cy = (w - 1) // 2, (h - 1) // 2
        dx = 0 if cx == sx else (1 if cx > sx else -1)
        dy = 0 if cy == sy else (1 if cy > sy else -1)
        if inb(sx + dx, sy + dy):
            return [dx, dy]
        if inb(sx + dx, sy):
            return [dx, 0]
        if inb(sx, sy + dy):
            return [0, dy]
        return [0, 0]

    def cheb(a, b):
        return max(abs(a[0] - b[0]), abs(a[1] - b[1]))

    # Prefer resources where we can arrive earlier (or at least not later than opponent).
    # Then choose move that improves that lead.
    best_cell = None
    best_key = None
    for rx, ry in res:
        self_d = cheb((sx, sy), (rx, ry))
        opp_d = cheb((ox, oy), (rx, ry))
        lead = opp_d - self_d  # higher is better
        # prefer meaningful lead, then closer resource
        key = (lead, -self_d, -opp_d, rx, ry)
        if best_key is None or key > best_key:
            best_key = key
            best_cell = (rx, ry)

    rx, ry = best_cell

    # One-step lookahead: for each legal move, maximize potential lead improvement,
    # and use attraction to target to avoid wandering.
    best_move = [0, 0]
    best_move_key = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        self_d2 = cheb((nx, ny), (rx, ry))
        opp_d2 = cheb((ox, oy), (rx, ry))
        lead2 = opp_d2 - self_d2
        # Small tie-breakers to reduce dithering near obstacles/edges
        to_target = self_d2
        # Also consider immediate blocking: discourage moving away from target
        delta_target = to_target - cheb((sx, sy), (rx, ry))
        key = (lead2, -to_target, -abs(dx) - abs(dy), -delta_target, dx, dy)
        if best_move_key is None or key > best_move_key:
            best_move_key = key
            best_move = [dx, dy]

    return [int(best_move[0]), int(best_move[1])]