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

    moves = [(-1,-1),(0,-1),(1,-1),(-1,0),(0,0),(1,0),(-1,1),(0,1),(1,1)]
    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obst
    def cheb(ax, ay, bx, by):
        a = ax - bx
        if a < 0: a = -a
        b = ay - by
        if b < 0: b = -b
        return a if a > b else b

    if not inb(sx, sy):
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if inb(nx, ny):
                return [dx, dy]
        return [0, 0]

    if not res:
        return [0, 0]

    moves = sorted(moves, key=lambda t: (t[0], t[1]))
    best_move = [0, 0]
    best_val = -10**9

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        # Intercept/steal: maximize (opp_dist - self_dist) to the best resource for us.
        best_for_move = -10**9
        for rx, ry in res:
            sd = cheb(nx, ny, rx, ry)
            od = cheb(ox, oy, rx, ry)
            steal = od - sd  # positive means we are closer
            if sd == 0:
                steal += 100  # prioritize grabbing immediately
            # Mild bias away from letting opponent grab sooner: penalize when opponent is strictly closer.
            if od < sd:
                steal -= 3
            if steal > best_for_move:
                best_for_move = steal
        # Small preference to move towards some resource when steal ties.
        # (deterministic: tie-break by best_for_move then by min self distance to any resource)
        min_sd = 10**9
        for rx, ry in res:
            d = cheb(nx, ny, rx, ry)
            if d < min_sd:
                min_sd = d
        val = best_for_move * 1000 - min_sd
        if val > best_val:
            best_val = val
            best_move = [dx, dy]

    return best_move