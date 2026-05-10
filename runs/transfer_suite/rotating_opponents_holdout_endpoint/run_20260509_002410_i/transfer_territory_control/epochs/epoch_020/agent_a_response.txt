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

    def manhattan(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    # Prefer capturing unclaimed cells adjacent to opponent territory (counter-claim pressure).
    opp_adj_targets = set()
    for (x, y) in opp_t:
        for dx, dy in dirs:
            nx, ny = x + dx, y + dy
            if inside(nx, ny) and (nx, ny) not in obstacles and (nx, ny) in unclaimed:
                opp_adj_targets.add((nx, ny))

    targets = list(opp_adj_targets) if opp_adj_targets else list(unclaimed)
    if targets:
        target = min(targets, key=lambda t: (manhattan((sx, sy), t), abs(t[0] - (w - 1)) + abs(t[1] - (h - 1))))
    else:
        target = (w // 2, h // 2)

    best = (float("-inf"), 0, 0)
    tx, ty = target
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inside(nx, ny) or (nx, ny) in obstacles:
            continue
        cell = (nx, ny)
        if cell in opp_t:
            cell_value = 2.0
        elif cell in unclaimed:
            cell_value = 1.0
        elif cell in self_t:
            cell_value = 0.0
        else:
            cell_value = -0.5

        dist_after = manhattan((nx, ny), (tx, ty))
        bonus = 0.4 if cell in opp_adj_targets else 0.0
        score = cell_value + bonus - 0.03 * dist_after - 0.001 * (nx + ny)
        if score > best[0]:
            best = (score, dx, dy)

    return [int(best[1]), int(best[2])]