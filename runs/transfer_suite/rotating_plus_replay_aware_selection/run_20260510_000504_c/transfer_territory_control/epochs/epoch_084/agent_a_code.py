def choose_move(observation):
    w = int(observation["grid_width"])
    h = int(observation["grid_height"])
    sx, sy = observation["self_position"]
    obstacles = set(map(tuple, observation.get("obstacles") or []))
    self_terr = set(map(tuple, observation.get("self_territory") or []))
    opp_terr = set(map(tuple, observation.get("opponent_territory") or []))
    unclaimed = set(map(tuple, observation.get("unclaimed_cells") or []))
    resources = observation.get("resources") or []
    dirs = [(-1,-1),(-1,0),(-1,1),(0,-1),(0,0),(0,1),(1,-1),(1,0),(1,1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def legal(x, y):
        return inb(x, y) and (x, y) not in obstacles

    if resources:
        tx, ty = resources[0]
        dx = 0 if tx == sx else (1 if tx > sx else -1)
        dy = 0 if ty == sy else (1 if ty > sy else -1)
        nx, ny = sx + dx, sy + dy
        if legal(nx, ny):
            return [dx, dy]

    # Precompute opponent territory presence for local distance heuristic
    opp_list = list(opp_terr) if opp_terr else []
    any_opp = bool(opp_list)

    def nearest_opp_dist(x, y):
        if not any_opp:
            return 99
        best = 99
        for ox, oy in opp_list:
            d = abs(ox - x) + abs(oy - y)
            if d < best:
                best = d
                if best == 0:
                    break
        return best

    # Heuristic: expand into unclaimed / near our territory while staying away from opponent
    def score_cell(nx, ny):
        if (nx, ny) in obstacles:
            return -10**9
        base = 0
        if (nx, ny) in unclaimed:
            base += 6
        if (nx, ny) in self_terr:
            base += 2
        if (nx, ny) in opp_terr:
            # Only take opponent cells if it improves local spacing; avoid unless very safe
            base -= 12
        # Prefer cells closer to unclaimed boundary that also increase our adjacency
        adj_self = 0
        adj_un = 0
        for ax, ay in dirs:
            xx, yy = nx + ax, ny + ay
            if not inb(xx, yy) or (xx, yy) in obstacles:
                continue
            if (xx, yy) in self_terr:
                adj_self += 1
            if (xx, yy) in unclaimed:
                adj_un += 1
        base += adj_self * 2 + adj_un * 1

        # Avoid entering opponent grab lines: maximize Manhattan distance to nearest opponent cell
        d = nearest_opp_dist(nx, ny)
        base += d * 0.9

        return base

    best_score = -10**18
    best_move = [0, 0]
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not legal(nx, ny):
            continue
        sc = score_cell(nx, ny)
        if sc > best_score:
            best_score = sc
            best_move = [dx, dy]
    return best_move