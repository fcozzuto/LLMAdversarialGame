def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation["resources"]
    obstacles = set((x, y) for x, y in observation["obstacles"])
    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def nearest_dist(x, y):
        if not resources:
            return 10**9
        best = 10**9
        for rx, ry in resources:
            d = abs(rx - x) + abs(ry - y)
            if d < best:
                best = d
        return best

    def nearest_idx(x, y):
        if not resources:
            return None
        bestd = 10**9
        besti = None
        for i, (rx, ry) in enumerate(resources):
            d = abs(rx - x) + abs(ry - y)
            if d < bestd or (d == bestd and (besti is None or i < besti)):
                bestd = d
                besti = i
        return besti

    cur_target_d = nearest_dist(sx, sy)
    best_score = None
    best_move = [0, 0]

    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue
        if (nx, ny) == (ox, oy):
            continue
        d = nearest_dist(nx, ny)
        opp_prox = max(abs(nx - ox), abs(ny - oy))  # Chebyshev distance
        score = (d, 5 * (cur_target_d - d) + (0 if opp_prox >= 2 else (2 - opp_prox)), (nx, ny))
        if best_score is None or score < best_score:
            best_score = score
            best_move = [dx, dy]

    if best_score is not None:
        return best_move

    # Fallback: avoid obstacles, move toward center
    cx, cy = (w - 1) // 2, (h - 1) // 2
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if inb(nx, ny) and (nx, ny) not in obstacles and (nx, ny) != (ox, oy):
            return [dx, dy]
    return [0, 0]