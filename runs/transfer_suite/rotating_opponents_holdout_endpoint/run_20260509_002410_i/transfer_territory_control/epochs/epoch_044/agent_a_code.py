def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sx, sy = observation.get("self_position") or [0, 0]
    ox, oy = observation.get("opponent_position") or [w - 1, h - 1]

    obstacles = set(map(tuple, observation.get("obstacles") or []))
    self_t = set(map(tuple, observation.get("self_territory") or []))
    opp_t = set(map(tuple, observation.get("opponent_territory") or []))
    unclaimed = set(map(tuple, observation.get("unclaimed_cells") or []))

    def inside(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def man(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    def adj_opp(x, y):
        c = 0
        for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            if (x + dx, y + dy) in opp_t:
                c += 1
        return c

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    cur = (sx, sy)
    opp_list = list(opp_t)
    best_score = None
    best_move = (0, 0)

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inside(nx, ny):
            continue
        n = (nx, ny)

        nearest_opp = 99
        if opp_list:
            nearest_opp = min(man(n, p) for p in opp_list)

        score = 0
        if n in opp_t:
            score += 240 - 2 * nearest_opp
        elif n in self_t:
            score += 12
        elif n in unclaimed:
            score += 75 - 6 * nearest_opp
        else:
            score += 18 - 3 * nearest_opp

        # If we're about to be "edge-cornered" near their boundary, lower commitment
        score -= 10 * adj_opp(nx, ny)

        # Prefer advancing in the direction that keeps us away from being immediately trapped
        score += 1.5 * (man(n, (ox, oy)) - man(cur, (ox, oy)))

        # Prefer moves that increase our edge-presence only when not adjacent to their boundary
        edge_dist = min(nx, ny, w - 1 - nx, h - 1 - ny)
        score += 2.0 * (3 - edge_dist) if adj_opp(nx, ny) == 0 else -2.0 * edge_dist

        if best_score is None or score > best_score or (score == best_score and (dx, dy) < best_move):
            best_score = score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]