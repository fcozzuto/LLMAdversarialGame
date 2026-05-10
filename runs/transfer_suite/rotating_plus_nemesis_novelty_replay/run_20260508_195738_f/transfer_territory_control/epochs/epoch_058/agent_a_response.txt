def choose_move(observation):
    x, y = observation.get("self_position", [0, 0])
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    obstacles = observation.get("obstacles", []) or []
    obs = set((p[0], p[1]) for p in obstacles)
    opp = set((p[0], p[1]) for p in (observation.get("opponent_territory", []) or []))
    unclaimed = set((p[0], p[1]) for p in (observation.get("unclaimed_cells", []) or []))
    selft = set((p[0], p[1]) for p in (observation.get("self_territory", []) or []))

    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def inb(nx, ny):
        return 0 <= nx < w and 0 <= ny < h

    opp_list = list(opp)
    def nearest_opp_dist(nx, ny):
        if not opp_list:
            return 10**9
        dmin = 10**9
        for (px, py) in opp_list:
            d = abs(px - nx) + abs(py - ny)
            if d < dmin:
                dmin = d
        return dmin

    def neighbor_has_opp(nx, ny):
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                if dx == 0 and dy == 0:
                    continue
                ax, ay = nx + dx, ny + dy
                if (ax, ay) in opp:
                    return True
        return False

    best_score = -10**18
    best_move = [0, 0]
    for dx, dy in dirs:
        nx, ny = x + dx, y + dy
        if not inb(nx, ny) or (nx, ny) in obs:
            continue
        score = 0.0
        if (nx, ny) in opp:
            score += 1000.0 - 5.0 * nearest_opp_dist(nx, ny)
        elif (nx, ny) in unclaimed:
            score += 80.0 + (1.5 if neighbor_has_opp(nx, ny) else 0.0) - 1.5 * nearest_opp_dist(nx, ny)
        elif (nx, ny) in selft:
            score += 5.0 - 0.2 * nearest_opp_dist(nx, ny)
        else:
            score += 20.0 - 1.0 * nearest_opp_dist(nx, ny)
            if neighbor_has_opp(nx, ny):
                score += 10.0
        # deterministic tie-break: prefer moves closer to opponent, then lower dx/dy lexicographically
        if score > best_score:
            best_score = score
            best_move = [dx, dy]
        elif score == best_score:
            if nearest_opp_dist(nx, ny) < nearest_opp_dist(x + best_move[0], y + best_move[1]):
                best_move = [dx, dy]
            elif (nearest_opp_dist(nx, ny) == nearest_opp_dist(x + best_move[0], y + best_move[1])
                  and (dx, dy) < (best_move[0], best_move[1])):
                best_move = [dx, dy]
    return best_move