def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w, h = observation["grid_width"], observation["grid_height"]
    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []
    obst = {(p[0], p[1]) for p in obstacles}
    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    turn = observation.get("turn_index", 0)

    def inb(x, y): return 0 <= x < w and 0 <= y < h

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def obst_adj_pen(x, y):
        if (x, y) in obst: return 10**6
        p = 0
        for nx, ny in ((x-1,y),(x+1,y),(x,y-1),(x,y+1),(x-1,y-1),(x+1,y+1),(x-1,y+1),(x+1,y-1)):
            if (nx, ny) in obst: p += 4
        return p

    if not resources:
        tx, ty = (w - 1) // 2, (h - 1) // 2
    else:
        best = None
        best_key = None
        for rx, ry in resources:
            ds = cheb(sx, sy, rx, ry)
            do = cheb(ox, oy, rx, ry)
            lead = do - ds
            key = (lead, -ds, -abs(rx - (w - 1 - ox)) - abs(ry - (h - 1 - oy)), rx, ry)
            if best_key is None or key > best_key:
                best_key = key
                best = (rx, ry)
        # If we can't beat the opponent to any resource, contest the one they're closest to.
        lead_best = best_key[0]
        if lead_best < 0 and len(resources) > 0:
            best_do = None
            best2 = None
            for rx, ry in resources:
                do = cheb(ox, oy, rx, ry)
                ds = cheb(sx, sy, rx, ry)
                key = (-do, ds, rx, ry)
                if best_do is None or key > best_do:
                    best_do = key
                    best2 = (rx, ry)
            best = best2
        tx, ty = best

    # One-step lookahead: maximize next lead (opponent distance constant to target).
    best_move = (0, 0)
    best_val = None
    opp_d = cheb(ox, oy, tx, ty)
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny): continue
        self_d_next = cheb(nx, ny, tx, ty)
        lead_next = opp_d - self_d_next
        # Small deterministic tie-break that changes policy over time to avoid stalling patterns.
        tie = -obst_adj_pen(nx, ny) + 0.01 * ((nx + 2*ny + (turn % 7)) - (sx + 2*sy))
        val = (lead_next, -self_d_next, tie)
        if best_val is None or val > best_val:
            best_val = val
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]