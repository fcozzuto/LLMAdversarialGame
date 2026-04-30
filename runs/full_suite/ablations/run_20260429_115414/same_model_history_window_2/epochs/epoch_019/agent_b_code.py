def choose_move(observation):
    w = observation["grid_width"]; h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources") or []
    obstacles = observation.get("obstacles") or []
    remaining = observation.get("remaining_resource_count", len(resources))

    blocked = set()
    for p in obstacles:
        if p and len(p) >= 2:
            blocked.add((p[0], p[1]))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def ok(x, y):
        return inb(x, y) and (x, y) not in blocked

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    moves = [(-1,-1),(-1,0),(-1,1),(0,-1),(0,0),(0,1),(1,-1),(1,0),(1,1)]
    legal = []
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if ok(nx, ny):
            legal.append((dx, dy, nx, ny))
    if not legal:
        return [0, 0]

    # Endgame: contest opponent corner deterministically
    if remaining <= 0 or not resources:
        tx, ty = (ox, oy)
        best = None; bestv = -10**18
        for dx, dy, nx, ny in legal:
            v = -cheb(nx, ny, tx, ty) - 0.1 * cheb(nx, ny, sx, sy)
            if v > bestv:
                bestv = v; best = (dx, dy)
        return [best[0], best[1]]

    # Greedy interception: choose move that maximizes advantage over opponent for the best resource
    best_move = (0, 0); bestv = -10**18; best_td = 10**18; best_od = -10**18
    for dx, dy, nx, ny in legal:
        best_gain = -10**18
        best_rx = nx; best_ry = ny
        for rx, ry in resources:
            sd = cheb(nx, ny, rx, ry)
            od = cheb(ox, oy, rx, ry)
            gain = od - sd  # positive means we are closer than opponent
            if gain > best_gain:
                best_gain = gain; best_rx = rx; best_ry = ry
        td = cheb(nx, ny, best_rx, best_ry)
        od2 = cheb(nx, ny, ox, oy)  # prefer not to get too close to opponent unless winning
        # Primary: maximize gain; secondary: minimize distance to chosen resource; tertiary: maximize distance from opponent
        v = best_gain * 10_000 - td * 10 - (-od2)
        if v > bestv or (v == bestv and (td < best_td or (td == best_td and od2 > best_od))):
            bestv = v; best_move = (dx, dy); best_td = td; best_od = od2

    return [int(best_move[0]), int(best_move[1])]