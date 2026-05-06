def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    x, y = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", [])
    obstacles = observation.get("obstacles", [])
    obstacle_set = set((a, b) for a, b in obstacles)

    dirs = [(-1, -1), (0, -1), (1, -1),
            (-1, 0), (0, 0), (1, 0),
            (-1, 1), (0, 1), (1, 1)]

    def inb(nx, ny):
        return 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacle_set

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    if not resources:
        best = [0, 0]
        bestv = -10**18
        for dx, dy in dirs:
            nx, ny = x + dx, y + dy
            if not inb(nx, ny):
                continue
            d = cheb(nx, ny, ox, oy)
            v = d * 1000 - (abs(nx - (w - 1)) + abs(ny - (h - 1)))
            if v > bestv or (v == bestv and (dx, dy) < (best[0], best[1])):
                bestv = v
                best = [dx, dy]
        return best

    def dist(ax, ay, bx, by):
        return abs(ax - bx) + abs(ay - by)

    best_move = [0, 0]
    best_score = -10**18
    for dx, dy in dirs:
        nx, ny = x + dx, y + dy
        if not inb(nx, ny):
            continue
        best_cell = -10**18
        for rx, ry in resources:
            ds = dist(nx, ny, rx, ry)
            do = dist(ox, oy, rx, ry)
            # Prefer cells where we can get it meaningfully before opponent; also avoid far targets
            v = (do - ds) * 1000 - ds
            if v > best_cell:
                best_cell = v
        # Mild tie-breaker: keep options and slightly increase distance from opponent
        opp_sep = cheb(nx, ny, ox, oy)
        v2 = best_cell * 10 + opp_sep
        if v2 > best_score or (v2 == best_score and (dx, dy) < (best_move[0], best_move[1])):
            best_score = v2
            best_move = [dx, dy]
    return best_move