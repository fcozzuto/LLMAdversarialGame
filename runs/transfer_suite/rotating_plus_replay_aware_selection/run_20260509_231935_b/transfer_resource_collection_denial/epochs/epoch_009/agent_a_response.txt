def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [w - 1, h - 1])
    resources = observation.get("resources", []) or []
    obstacles_list = observation.get("obstacles", []) or []
    obstacles = set((p[0], p[1]) for p in obstacles_list)

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def dist8(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy  # Chebyshev distance

    if not resources:
        cx, cy = w // 2, h // 2
        best = (10**18, 0, 0)
        for dx, dy in ((0,0),(1,0),(-1,0),(0,1),(0,-1),(1,1),(1,-1),(-1,1),(-1,-1)):
            nx, ny = sx + dx, sy + dy
            if not inb(nx, ny) or (nx, ny) in obstacles:
                nx, ny = sx, sy
            d = dist8(nx, ny, cx, cy)
            if (d, -nx, -ny) < best:
                best = (d, dx, dy)
        return [best[1], best[2]]

    res_set = set((p[0], p[1]) for p in resources)
    dirs = ((0,0),(1,0),(-1,0),(0,1),(0,-1),(1,1),(1,-1),(-1,1),(-1,-1))

    best_score = -10**18
    best_move = (0, 0)

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            nx, ny = sx, sy

        immediate = 1 if (nx, ny) in res_set else 0
        # Race: maximize (opponent arrival time - self arrival time) for the resource we contest best.
        best_for_move = -10**18
        for rx, ry in res_set:
            self_d = dist8(nx, ny, rx, ry)
            opp_d = dist8(ox, oy, rx, ry)
            lead = opp_d - self_d
            score = lead * 100 - self_d
            if self_d == 0:
                score += 10**8
            if score > best_for_move:
                best_for_move = score

        # Small bias: if already tied, move closer to the best-lead resource.
        total_score = best_for_move + (immediate * 1000) - (dist8(nx, ny, ox, oy) // 4)
        if total_score > best_score:
            best_score = total_score
            best_move = (dx, dy)

    return [best_move[0], best_move[1]]