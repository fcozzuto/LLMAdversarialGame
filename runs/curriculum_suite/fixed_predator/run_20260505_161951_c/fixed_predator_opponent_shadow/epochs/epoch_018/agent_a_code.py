def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    gw, gh = observation["grid_width"], observation["grid_height"]
    obstacles = set(tuple(p) for p in observation.get("obstacles", []))
    resources = [tuple(p) for p in observation.get("resources", [])]

    def inb(x, y):
        return 0 <= x < gw and 0 <= y < gh

    legal = []
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            if inb(nx, ny) and (nx, ny) not in obstacles:
                legal.append((dx, dy, nx, ny))
    if not legal:
        return [0, 0]

    def man(ax, ay, bx, by):
        return abs(ax - bx) + abs(ay - by)

    if not resources:
        best = None
        bestv = -10**18
        for dx, dy, nx, ny in legal:
            v = man(nx, ny, ox, oy)
            if v > bestv:
                bestv = v
                best = (dx, dy)
        return [best[0], best[1]]

    best_move = None
    best_val = -10**18
    best_sd = None
    for dx, dy, nx, ny in legal:
        # Choose the resource that gives us the strongest "closer than opponent" advantage after this move.
        # Also slightly prefer being closer in absolute terms to reduce time-to-capture once we commit.
        cur_best = -10**18
        cur_sd = 10**18
        for rx, ry in resources:
            sd = man(nx, ny, rx, ry)
            od = man(ox, oy, rx, ry)
            val = (od - sd) * 100 - sd
            if val > cur_best or (val == cur_best and sd < cur_sd):
                cur_best = val
                cur_sd = sd
        if cur_best > best_val or (cur_best == best_val and cur_sd < best_sd):
            best_val = cur_best
            best_sd = cur_sd
            best_move = (dx, dy)

    return [best_move[0], best_move[1]]