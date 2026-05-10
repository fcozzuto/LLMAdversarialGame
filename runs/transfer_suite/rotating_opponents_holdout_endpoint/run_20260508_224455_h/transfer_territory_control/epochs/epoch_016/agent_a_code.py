def choose_move(observation):
    sx, sy = observation["self_position"]
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    obstacles = set(map(tuple, observation.get("obstacles", [])))
    self_t = set(map(tuple, observation.get("self_territory", [])))
    opp_t = set(map(tuple, observation.get("opponent_territory", [])))
    unclaimed = set(map(tuple, observation.get("unclaimed_cells", [])))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    # Precompute nearest unclaimed (deterministic)
    nearest_un = None
    if unclaimed:
        best = None
        for (x, y) in unclaimed:
            d = abs(x - sx) + abs(y - sy)
            cand = (d, x, y)
            if best is None or cand < best:
                best = cand
                best_xy = (x, y)
        nearest_un = best_xy

    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    best_move = (0, 0)
    best_score = None

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            score = -10**9
        else:
            cell = (nx, ny)
            score = 0
            if cell in unclaimed:
                score += 12
            if cell in opp_t:
                score += 7
            if cell in self_t:
                score += 2

            if nearest_un is not None:
                score += (abs(nearest_un[0] - sx) + abs(nearest_un[1] - sy)) - (abs(nearest_un[0] - nx) + abs(nearest_un[1] - ny))
            else:
                if opp_t:
                    # Nudge toward opponent territory
                    bestd = None
                    for (ox, oy) in opp_t:
                        d = abs(ox - nx) + abs(oy - ny)
                        if bestd is None or d < bestd:
                            bestd = d
                    score += -bestd * 0.1

            # Small deterministic preference to avoid dithering: favor moves that keep/advance x then y
            score += (1 if dx != 0 else 0) * 0.01 + (1 if dy != 0 else 0) * 0.001

        if best_score is None or score > best_score or (score == best_score and (dx, dy) < best_move):
            best_score = score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]