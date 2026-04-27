def choose_move(observation):
    turn = observation.get("turn_index", 0)
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)

    me = observation.get("self_position", [0, 0])
    opp = observation.get("opponent_position", [0, 0])
    resources = observation.get("resources", []) or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))

    def in_bounds(x, y):
        return 0 <= x < w and 0 <= y < h

    moves = [(-1,-1),(0,-1),(1,-1),(-1,0),(0,0),(1,0),(-1,1),(0,1),(1,1)]

    def dist_manhattan(a, b):
        return abs(a[0]-b[0]) + abs(a[1]-b[1])

    def score_move(nx, ny):
        if not in_bounds(nx, ny) or (nx, ny) in obstacles:
            return -10**6
        sc = 0
        for rx, ry in resources:
            d_my = dist_manhattan((nx, ny), (rx, ry))
            d_opp = dist_manhattan((opp[0], opp[1]), (rx, ry))
            sc += (d_opp - d_my)  # prefer positions that bring us closer to resources than opponent
        # discourage staying if opponent is closer to resource
        return sc

    best = [0, 0]
    best_score = -10**9

    # If resources exist, try to move toward best candidate resource
    if resources:
        for dx, dy in moves:
            nx, ny = me[0] + dx, me[1] + dy
            s = score_move(nx, ny)
            if s > best_score:
                best_score = s
                best = [dx, dy]

        if best_score <= 0:
            # fallback: move toward opponent to contest space
            ox, oy = opp[0], opp[1]
            best = [0, 0]
            best_dist = 10**9
            for dx, dy in moves:
                nx, ny = me[0] + dx, me[1] + dy
                if not in_bounds(nx, ny) or (nx, ny) in obstacles:
                    continue
                d = dist_manhattan((nx, ny), (ox, oy))
                if d < best_dist:
                    best_dist = d
                    best = [dx, dy]
        # ensure integer
        return [int(best[0]), int(best[1])]
    else:
        # No resources: move toward opponent while avoiding obstacles
        ox, oy = opp[0], opp[1]
        best = [0, 0]
        best_score = -10**9
        for dx, dy in moves:
            nx, ny = me[0] + dx, me[1] + dy
            if not in_bounds(nx, ny) or (nx, ny) in obstacles:
                continue
            d = dist_manhattan((nx, ny), (ox, oy))
            # prefer reducing distance to opponent
            if d < best_score:
                best_score = d
                best = [dx, dy]
        return [int(best[0]), int(best[1])]