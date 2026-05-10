def choose_move(observation):
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []
    obs = set((int(x), int(y)) for x, y in obstacles)

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0:
            dx = -dx
        dy = y1 - y2
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    best_move = (0, 0)
    best_val = (-10**18, -10**18)

    # Pre-filter resources to those we can potentially move onto soon (deterministic heuristic).
    res = []
    for rx, ry in resources:
        rx, ry = int(rx), int(ry)
        if inb(rx, ry) and (rx, ry) not in obs:
            res.append((rx, ry))
    if not res:
        return [0, 0]

    # Choose move that maximizes our "relative advantage" over opponent for the best resource.
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obs:
            continue
        cur_best = (-10**18, -10**18)
        for rx, ry in res:
            sd = cheb(nx, ny, rx, ry)
            od = cheb(ox, oy, rx, ry)
            # prioritize resources where opponent is relatively closer, but we move to reduce that gap
            # key1: (od - sd) after our move; key2: smaller sd
            val = (od - sd, -sd)
            if val > cur_best:
                cur_best = val
        if cur_best > best_val:
            best_val = cur_best
            best_move = (dx, dy)

    # If all candidate moves were invalid (rare due to engine keep-in-place), stay.
    return [int(best_move[0]), int(best_move[1])]