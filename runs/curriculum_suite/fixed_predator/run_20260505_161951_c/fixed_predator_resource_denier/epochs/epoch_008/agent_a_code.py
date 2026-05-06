def choose_move(observation):
    x, y = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w, h = observation["grid_width"], observation["grid_height"]
    resources = observation.get("resources", [])
    obstacles = observation.get("obstacles", [])
    obs = set((a, b) for a, b in obstacles)
    dirs = [(dx, dy) for dx in (-1, 0, 1) for dy in (-1, 0, 1)]

    def inb(nx, ny):
        return 0 <= nx < w and 0 <= ny < h

    def cheb(a, b, c, d):
        da = a - c
        if da < 0:
            da = -da
        db = b - d
        if db < 0:
            db = -db
        return da if da > db else db

    def best_resource_score(px, py):
        if not resources:
            return -10**9
        best = -10**18
        for rx, ry in resources:
            sd = cheb(px, py, rx, ry)
            od = cheb(ox, oy, rx, ry)
            val = (od - sd) * 1000 - sd * 2
            if sd == 0:
                val += 1000000
            if val > best:
                best = val
        return best

    best_move = (0, 0)
    best_val = -10**18

    if not resources:
        for dx, dy in dirs:
            nx, ny = x + dx, y + dy
            if not inb(nx, ny) or (nx, ny) in obs:
                continue
            d = cheb(nx, ny, ox, oy)
            val = d * 10 - (1 if dx == 0 and dy == 0 else 0)
            if val > best_val or (val == best_val and (dx, dy) < best_move):
                best_val = val
                best_move = (dx, dy)
        return [best_move[0], best_move[1]]

    for dx, dy in dirs:
        nx, ny = x + dx, y + dy
        if not inb(nx, ny) or (nx, ny) in obs:
            continue
        val = best_resource_score(nx, ny)
        # small tie-break: prefer moving closer to opponent (deny) if equally good
        val -= cheb(nx, ny, ox, oy)
        if val > best_val or (val == best_val and (dx, dy) < best_move):
            best_val = val
            best_move = (dx, dy)

    if best_move == (0, 0):
        # ensure we return a valid safe move; otherwise stay
        if (x, y) in obs or not inb(x, y):
            return [0, 0]
    return [best_move[0], best_move[1]]