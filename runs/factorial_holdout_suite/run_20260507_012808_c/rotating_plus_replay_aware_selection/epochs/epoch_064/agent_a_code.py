def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", []) or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))

    dirs = [(-1,-1),(0,-1),(1,-1),(-1,0),(0,0),(1,0),(-1,1),(0,1),(1,1)]

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def dist(x1, y1, x2, y2):
        return max(abs(x2 - x1), abs(y2 - y1))

    res_list = [tuple(r) for r in resources]
    if not res_list:
        tx, ty = (w - 1) // 2, (h - 1) // 2
        dx = 0 if tx == sx else (1 if tx > sx else -1)
        dy = 0 if ty == sy else (1 if ty > sy else -1)
        nx, ny = sx + dx, sy + dy
        return [dx, dy] if valid(nx, ny) else [0, 0]

    best_dx, best_dy = 0, 0
    best_val = -10**18

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue

        # Strongly favor cells that create the best "grab-first" margin on any resource.
        # If margins are poor, still drift to a nearest resource while respecting opponent races.
        best_margin = -10**9
        best_tie = 10**9
        for rx, ry in res_list:
            sd = dist(nx, ny, rx, ry)
            od = dist(ox, oy, rx, ry)
            margin = od - sd  # >0 means we can reach earlier
            # Prefer larger margin; if equal, prefer smaller self distance.
            if margin > best_margin or (margin == best_margin and sd < best_tie):
                best_margin = margin
                best_tie = sd

        # Objective: dominate by margin; penalize being farther.
        val = best_margin * 1000 - best_tie

        if val > best_val:
            best_val = val
            best_dx, best_dy = dx, dy

    return [int(best_dx), int(best_dy)]