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

    # Find frontier unclaimed adjacent to our territory (often best vs counterclaimers)
    dirs4 = [(-1, 0), (1, 0), (0, -1), (0, 1)]
    frontier = []
    if self_t and unclaimed:
        for x, y in self_t:
            for dx, dy in dirs4:
                nx, ny = x + dx, y + dy
                if (nx, ny) in unclaimed:
                    frontier.append((nx, ny))
        if frontier:
            targets = frontier
        else:
            targets = list(unclaimed)
    else:
        targets = list(unclaimed)

    # If no unclaimed, expand toward opponent territory
    if not targets:
        targets = list(opp_t) if opp_t else [(sx, sy)]

    # Deterministic target: nearest to us; tie-break by lexicographic position
    def manh(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    target = min(targets, key=lambda p: (manh((sx, sy), p), p[0], p[1]))

    opp_bias = min(1.0, 0.02 * max(0, observation.get("opponent_territory_count", 0)))
    dirs8 = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    best = (0, 0)
    best_val = -10**18

    for dx, dy in dirs8:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue
        cell = (nx, ny)

        # Immediate gain heuristic (occupy flips on entry, so treat opponent-owned as gain)
        cell_gain = 0
        if cell in unclaimed:
            cell_gain = 1.5
        elif cell in opp_t:
            cell_gain = 1.0
        elif cell in self_t:
            cell_gain = 0.2
        else:
            cell_gain = 0.5  # unknown/unlisted: still likely neutral-ish

        # Progress to target
        dist = manh((nx, ny), target)

        # Avoid stepping too directly onto opponent if target is already ours/nearby
        ox, oy = observation["opponent_position"]
        opp_dist = abs(ox - nx) + abs(oy - ny)

        val = cell_gain * 10.0 + (-dist) * 0.8 + opp_dist * opp_bias
        if val > best_val:
            best_val = val
            best = (dx, dy)

    if best_val == -10**18:
        return [0, 0]
    return [int(best[0]), int(best[1])]