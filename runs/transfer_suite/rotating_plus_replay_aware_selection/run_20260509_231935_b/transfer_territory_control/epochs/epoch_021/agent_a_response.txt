def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    obs_list = observation.get("obstacles") or []
    obstacles = set((p[0], p[1]) for p in obs_list)

    un_list = observation.get("unclaimed_cells") or []
    unclaimed = set((p[0], p[1]) for p in un_list)

    opp_list = observation.get("opponent_territory") or []
    opponent_territory = set((p[0], p[1]) for p in opp_list)

    self_list = observation.get("self_territory") or []
    self_territory = set((p[0], p[1]) for p in self_list)

    ox0, oy0 = observation.get("opponent_position") or (None, None)

    def dist_to_set(x, y, s):
        if not s:
            return 10**9
        best = 10**9
        for a, b in s:
            d = abs(x - a) + abs(y - b)
            if d < best:
                best = d
        return best

    def in_bounds(x, y):
        return 0 <= x < w and 0 <= y < h

    best_move = [0, 0]
    best_score = -10**18

    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            if not in_bounds(nx, ny) or (nx, ny) in obstacles:
                continue

            score = 0

            if (nx, ny) in opponent_territory:
                d_opp = (abs(nx - ox0) + abs(ny - oy0)) if ox0 is not None else 0
                score += 900 - 3 * d_opp
            elif (nx, ny) in unclaimed:
                score += 1000
                score += -2 * dist_to_set(nx, ny, unclaimed)
            elif (nx, ny) in self_territory:
                score += 120
                score += -1 * dist_to_set(nx, ny, unclaimed)
            else:
                score += 60 - 2 * dist_to_set(nx, ny, unclaimed)

            d_opp_terr = dist_to_set(nx, ny, opponent_territory)
            if opponent_territory:
                score += -2 * d_opp_terr

            if (dx, dy) == (0, 0):
                score -= 5

            if score > best_score:
                best_score = score
                best_move = [dx, dy]

    return [int(best_move[0]), int(best_move[1])]