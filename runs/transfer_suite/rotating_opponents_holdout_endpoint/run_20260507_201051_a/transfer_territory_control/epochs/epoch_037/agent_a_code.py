def choose_move(observation):
    w = int(observation["grid_width"])
    h = int(observation["grid_height"])
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]

    obstacles = set(map(tuple, observation.get("obstacles") or []))
    unclaimed = set(map(tuple, observation.get("unclaimed_cells") or []))
    self_t = set(map(tuple, observation.get("self_territory") or []))
    opp_t = set(map(tuple, observation.get("opponent_territory") or []))

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    neigh = [(-1, -1), (0, -1), (1, -1), (-1, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def any_adj_in(x, y, S):
        for ax, ay in neigh:
            if (x + ax, y + ay) in S:
                return True
        return False

    def adj_count_in(x, y, S):
        c = 0
        for ax, ay in neigh:
            if (x + ax, y + ay) in S:
                c += 1
        return c

    best = (-10**18, [0, 0])
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue

        score = 0
        if (nx, ny) in opp_t:
            score += 2000
        elif (nx, ny) in unclaimed:
            score += 20
        elif (nx, ny) in self_t:
            score += 2

        if any_adj_in(nx, ny, opp_t):
            score += 15 + 2 * adj_count_in(nx, ny, opp_t)
        if any_adj_in(nx, ny, unclaimed):
            score += 6

        # Avoid stepping right next to opponent unless it flips immediately
        if not ((nx, ny) in opp_t) and (abs(nx - ox) <= 1 and abs(ny - oy) <= 1):
            score -= 25

        # Slightly prefer reducing distance to opponent when advancing front
        score -= (abs(nx - ox) + abs(ny - oy)) * 0.5

        if score > best[0]:
            best = (score, [dx, dy])

    return best[1]