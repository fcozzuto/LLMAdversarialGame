def choose_move(observation):
    w, h = observation["grid_width"], observation["grid_height"]
    sx, sy = observation["self_position"]
    obstacles = set(tuple(p) for p in (observation.get("obstacles") or []))
    unclaimed = set(tuple(p) for p in (observation.get("unclaimed_cells") or []))
    self_t = set(tuple(p) for p in (observation.get("self_territory") or []))
    opp_t = set(tuple(p) for p in (observation.get("opponent_territory") or []))

    dirs = [(-1, -1), (-1, 0), (-1, 1),
            (0, -1), (0, 0), (0, 1),
            (1, -1), (1, 0), (1, 1)]

    def inside(nx, ny):
        return 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles

    def adj_counts(nx, ny):
        s_adj = 0
        o_adj = 0
        u_adj = 0
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                if dx == 0 and dy == 0:
                    continue
                p = (nx + dx, ny + dy)
                if not (0 <= p[0] < w and 0 <= p[1] < h):
                    continue
                if p in self_t:
                    s_adj += 1
                elif p in opp_t:
                    o_adj += 1
                elif p in unclaimed:
                    u_adj += 1
        return s_adj, o_adj, u_adj

    best = [0, 0]
    best_score = -10**18

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inside(nx, ny):
            continue
        target = (nx, ny)
        s_adj, o_adj, u_adj = adj_counts(nx, ny)

        if target in self_t:
            score = 2 + s_adj - o_adj
        elif target in opp_t:
            score = 30 + 3 * s_adj + 2 * o_adj
        elif target in unclaimed:
            # push outward from own frontier, but avoid stepping into opponent's immediate neighborhood
            score = 10 + 2 * s_adj + u_adj - 3 * o_adj
        else:
            # rare: empty but not unclaimed (treated like neutral)
            score = 1 + s_adj - o_adj

        # encourage moving off-still when stuck in our territory
        if dx == 0 and dy == 0:
            score -= 1 if target in self_t else 0

        if score > best_score:
            best_score = score
            best = [dx, dy]

    return best