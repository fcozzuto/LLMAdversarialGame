def choose_move(observation):
    w = observation["grid_width"]; h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources") or []
    obstacles = observation.get("obstacles") or []
    rem = observation.get("remaining_resource_count", len(resources))
    blocked = set()
    for p in obstacles:
        if p and len(p) >= 2:
            blocked.add((p[0], p[1]))

    def inb(x, y): return 0 <= x < w and 0 <= y < h
    def ok(x, y): return inb(x, y) and (x, y) not in blocked
    def cheb(x1, y1, x2, y2):
        dx = x1 - x2; dx = -dx if dx < 0 else dx
        dy = y1 - y2; dy = -dy if dy < 0 else dy
        return dx if dx > dy else dy

    moves = [(-1,-1),(-1,0),(-1,1),(0,-1),(0,0),(0,1),(1,-1),(1,0),(1,1)]
    best_move = (0, 0)
    best_val = -10**18
    turn = observation.get("turn_index", 0) & 1

    if not resources or rem <= 0:
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not ok(nx, ny): 
                continue
            v = 2.0 * cheb(nx, ny, ox, oy) - 1.0 * cheb(nx, ny, sx, sy)
            if v > best_val or (v == best_val and (dx, dy) < best_move):
                best_val = v; best_move = (dx, dy)
        return [best_move[0], best_move[1]]

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not ok(nx, ny):
            continue
        # Evaluate best target from this next position
        cur_best = -10**18
        for rx, ry in resources:
            if (rx, ry) in blocked:
                continue
            d_self = cheb(nx, ny, rx, ry)
            d_opp = cheb(ox, oy, rx, ry)
            # advantage: get resource sooner; add small tie-breakers
            adv = d_opp - d_self
            # encourage moving toward relatively "safe" resources (not behind obstacles by simple proxy)
            prox = -0.05 * cheb(nx, ny, sx, sy)
            tie = -0.001 * ((rx + 3*ry) + (turn * 7))
            score = (10.0 * adv) + prox + tie
            if score > cur_best:
                cur_best = score
        # Mildly prefer staying closer to opponent when resources are scarce (to deny)
        scarcity = 1.0 if rem <= 4 else 0.0
        deny = scarcity * (cheb(nx, ny, ox, oy) * -0.2)
        v = cur_best + deny
        if v > best_val or (v == best_val and (dx, dy) < best_move):
            best_val = v; best_move = (dx, dy)

    return [best_move[0], best_move[1]]