def choose_move(observation):
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    w = observation.get("grid_width", 1)
    h = observation.get("grid_height", 1)

    obstacles_list = observation.get("obstacles", []) or []
    obstacles = set((p[0], p[1]) for p in obstacles_list)

    self_cells = set((p[0], p[1]) for p in (observation.get("self_territory", []) or []))
    opp_cells = set((p[0], p[1]) for p in (observation.get("opponent_territory", []) or []))
    unclaimed = set((p[0], p[1]) for p in (observation.get("unclaimed_cells", []) or []))

    neigh = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best_move = [0, 0]
    best_score = -10**18

    def inside(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    for dx, dy in neigh:
        nx, ny = sx + dx, sy + dy
        if not inside(nx, ny):
            continue
        if (nx, ny) in opp_cells:
            continue

        dist_to_opp = (nx - ox) * (nx - ox) + (ny - oy) * (ny - oy)
        dist_to_self = (nx - sx) * (nx - sx) + (ny - sy) * (ny - sy)
        edge_bias = min(nx, ny, w - 1 - nx, h - 1 - ny)

        score = 0
        if (nx, ny) in unclaimed:
            score += 300
        if (nx, ny) in self_cells:
            score += 80
        score += -dist_to_opp // 2
        score += edge_bias // 3
        score += -dist_to_self // 10

        if score > best_score:
            best_score = score
            best_move = [dx, dy]

    if best_move == [0, 0] and not inside(sx, sy):
        for dx, dy in neigh:
            nx, ny = sx + dx, sy + dy
            if inside(nx, ny) and (nx, ny) not in opp_cells:
                return [dx, dy]
    return best_move