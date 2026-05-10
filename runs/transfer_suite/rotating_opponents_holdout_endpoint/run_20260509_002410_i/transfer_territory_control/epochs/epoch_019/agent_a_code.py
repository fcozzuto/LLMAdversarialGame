def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation.get("self_position", (0, 0))
    obstacles = set(map(tuple, observation.get("obstacles") or []))
    self_t = set(map(tuple, observation.get("self_territory") or []))
    opp_t = set(map(tuple, observation.get("opponent_territory") or []))
    unclaimed = set(map(tuple, observation.get("unclaimed_cells") or []))

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def inside(x, y):
        return 0 <= x < w and 0 <= y < h

    def dist(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    # Choose target: prioritize nearest unclaimed adjacent to opponent (counterclaim), else nearest unclaimed, else center-ish.
    opp_adj = set()
    for (x, y) in opp_t:
        for dx, dy in dirs:
            nx, ny = x + dx, y + dy
            if inside(nx, ny) and (nx, ny) not in obstacles and (nx, ny) in unclaimed:
                opp_adj.add((nx, ny))

    targets = None
    if opp_adj:
        targets = list(opp_adj)
    elif unclaimed:
        targets = list(unclaimed)
    else:
        targets = [(w // 2, h // 2), (w - 1, h - 1), (0, h - 1), (w - 1, 0)]

    target = min(targets, key=lambda t: (dist((sx, sy), t), abs(t[0] - (w - 1)) + abs(t[1] - (h - 1))))

    opp_count = int(observation.get("opponent_territory_count", len(opp_t)))
    self_count = int(observation.get("self_territory_count", len(self_t)))
    aggressive = 1.0 if opp_count >= self_count else 0.6

    best = [0, 0]
    best_score = -10**18
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inside(nx, ny) or (nx, ny) in obstacles:
            continue

        s = 0.0
        if (nx, ny) in opp_t:
            s += 12.0 * aggressive
        elif (nx, ny) in unclaimed:
            s += 7.0
        elif (nx, ny) in self_t:
            s += 2.0
        else:
            s -= 1.0

        # Move toward target
        d_to_t = dist((nx, ny), target)
        s += 3.0 / (1 + d_to_t)

        # Avoid moving away from current territory if already ahead
        if self_count > opp_count:
            s += 0.7 / (1 + dist((nx, ny), (sx, sy)))

        # Slight preference for progressing toward target direction (deterministic tie-breaker)
        tie = (0, 0)
        if d_to_t < dist((sx, sy), target):
            s += 0.2
        tie = (abs(nx - target[0]) + abs(ny - target[1]), abs(nx - (w - 1)) + abs(ny - (h - 1)))

        if s > best_score or (s == best_score and tie < (abs(best[0] + sx - target[0]) + abs(best[1] + sy - target[1]),
                                                            abs(best[0] + sx - (w - 1)) + abs(best[1] + sy - (h - 1)))):
            best_score = s
            best = [dx, dy]

    return [int(best[0]), int(best[1])]