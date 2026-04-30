def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    obstacles = set((x, y) for x, y in observation["obstacles"])
    resources = observation["resources"]

    cand = [(-1, -1), (-1, 0), (-1, 1),
            (0, -1), (0, 0), (0, 1),
            (1, -1), (1, 0), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def dist(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    best_score = None
    best_move = [0, 0]
    for dx, dy in cand:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            score = -10**9
        else:
            # Evaluate best "advantage" resource we could head for next step.
            score = -10**9
            for rx, ry in resources:
                if (rx, ry) in obstacles:
                    continue
                self_d = abs(nx - rx) + abs(ny - ry)
                opp_d = abs(ox - rx) + abs(oy - ry)
                adv = opp_d - self_d  # positive means we are closer
                # Collecting immediately is strongly preferred.
                if nx == rx and ny == ry:
                    adv += 1000
                val = adv * 100 - self_d
                if val > score:
                    score = val
            # Small deterrent for moving away from any resource advantage.
            if score < -10**8:
                score = -10**8 + (-abs(nx - sx) - abs(ny - sy))
        if best_score is None or score > best_score:
            best_score = score
            best_move = [dx, dy]
    return [int(best_move[0]), int(best_move[1])]