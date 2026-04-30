def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    x, y = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", [])
    obstacles = observation.get("obstacles", [])
    obs_set = set((a, b) for a, b in obstacles)

    deltas = [(-1,-1),(0,-1),(1,-1),(-1,0),(0,0),(1,0),(-1,1),(0,1),(1,1)]
    def inb(nx, ny):
        return 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obs_set

    def manh(ax, ay, bx, by):
        d = ax - bx
        if d < 0: d = -d
        e = ay - by
        if e < 0: e = -e
        return d + e

    def best_value(px, py):
        if not resources:
            return -manh(px, py, ox, oy)  # fallback: approach opponent slightly
        best = -10**9
        for rx, ry in resources:
            myd = manh(px, py, rx, ry)
            opd = manh(ox, oy, rx, ry)
            if myd == 0:
                val = 100000
            else:
                val = (opd - myd) * 2 - myd * 0.25
            # small bias to move away from obstacles already handled by filtering moves
            if val > best:
                best = val
        return best

    best_move = (0, 0)
    best_eval = -10**18
    base_val = best_value(x, y)

    for dx, dy in deltas:
        nx, ny = x + dx, y + dy
        if not inb(nx, ny):
            continue
        ev = best_value(nx, ny)
        # encourage movement when not improving too little
        if (dx, dy) != (0, 0) and ev < base_val - 0.5:
            ev -= 0.1
        if ev > best_eval:
            best_eval = ev
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]