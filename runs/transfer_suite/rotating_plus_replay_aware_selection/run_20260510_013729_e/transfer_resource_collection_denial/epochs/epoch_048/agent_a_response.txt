def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w, h = observation["grid_width"], observation["grid_height"]
    resources = observation.get("resources") or []
    obstacles = observation.get("obstacles") or []
    if not resources:
        return [0, 0]

    obst = {(x, y) for x, y in obstacles}
    cand = [(-1,-1),(-1,0),(-1,1),(0,-1),(0,0),(0,1),(1,-1),(1,0),(1,1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def cheb(x1, y1, x2, y2):
        dx = x2 - x1
        if dx < 0: dx = -dx
        dy = y2 - y1
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    # Deterministic ordering to break ties consistently
    resources_sorted = sorted(resources, key=lambda p: (p[0] * 8 + p[1], p[0], p[1]))

    def eval_cell(x, y):
        best = -10**9
        for rx, ry in resources_sorted:
            ds = cheb(x, y, rx, ry)
            do = cheb(ox, oy, rx, ry)
            cap = 3.0 if (x, y) == (rx, ry) else 0.0
            # Prefer resources where we are ahead; when equal, prefer nearer.
            # Add small bonus for being farther from opponent for that resource (denial).
            lead = (do - ds)
            val = cap + 2.2 * lead - 0.35 * ds + 0.08 * cheb(x, y, ox, oy)
            if val > best:
                best = val
        # Mild wall/obstacle penalty for staying in place when invalid moves occur
        if (x, y) in obst:
            best -= 1000
        return best

    best_move = (0, 0)
    best_val = -10**18
    for dx, dy in cand:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            nx, ny = sx, sy  # deterministic: invalid move effectively stays
        v = eval_cell(nx, ny)
        # Tie-break: prefer captures, then higher v, then lexicographically smaller move
        if v > best_val:
            best_val = v
            best_move = (dx, dy)
        elif v == best_val:
            if (dx, dy) < best_move:
                best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]