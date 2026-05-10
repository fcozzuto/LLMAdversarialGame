def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w, h = observation["grid_width"], observation["grid_height"]
    obstacles = set((p[0], p[1]) for p in observation.get("obstacles", []))
    self_cells = set((p[0], p[1]) for p in observation.get("self_territory", []))
    opp_cells = set((p[0], p[1]) for p in observation.get("opponent_territory", []))
    unclaimed = set((p[0], p[1]) for p in observation.get("unclaimed_cells", []))

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    neigh8 = deltas

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def man(a, b, c, d):
        return abs(a - c) + abs(b - d)

    def obstacle_risk(x, y):
        r = 0
        for dx, dy in neigh8:
            nx, ny = x + dx, y + dy
            if not (0 <= nx < w and 0 <= ny < h) or (nx, ny) in obstacles:
                r += 1
        return r

    best_score = -10**18
    best_move = (0, 0)
    order = {d: i for i, d in enumerate(deltas)}

    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue

        if (nx, ny) in self_cells:
            score = 3.0
        elif (nx, ny) in opp_cells:
            score = 60.0 - 0.6 * man(nx, ny, ox, oy)
        elif (nx, ny) in unclaimed:
            adj_opp = 0
            for px, py in neigh8:
                ax, ay = nx + px, ny + py
                if 0 <= ax < w and 0 <= ay < h and (ax, ay) in opp_cells:
                    adj_opp += 1
            dist = man(nx, ny, ox, oy)
            score = 12.0 + 3.0 * adj_opp - 0.08 * dist
        else:
            # unknown cells: treat like low-value expansion
            score = 1.0 - 0.05 * man(nx, ny, ox, oy)

        score -= 0.35 * obstacle_risk(nx, ny)

        if score > best_score or (score == best_score and order[(dx, dy)] < order[best_move]):
            best_score = score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]