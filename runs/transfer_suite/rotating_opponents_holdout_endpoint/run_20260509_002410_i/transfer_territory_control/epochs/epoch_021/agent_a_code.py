def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation.get("self_position", (0, 0))
    obstacles = set(map(tuple, observation.get("obstacles") or []))
    self_t = set(map(tuple, observation.get("self_territory") or []))
    opp_t = set(map(tuple, observation.get("opponent_territory") or []))
    unclaimed = set(map(tuple, observation.get("unclaimed_cells") or []))

    def inside(x, y):
        return 0 <= x < w and 0 <= y < h

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    def manhattan(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    # Target: unclaimed cell adjacent to opponent territory (most forcing), else nearest unclaimed, else center.
    opp_adj = set()
    for (x, y) in opp_t:
        for dx, dy in dirs:
            nx, ny = x + dx, y + dy
            if inside(nx, ny) and (nx, ny) not in obstacles and (nx, ny) in unclaimed:
                opp_adj.add((nx, ny))
    if opp_adj:
        targets = list(opp_adj)
    elif unclaimed:
        targets = list(unclaimed)
    else:
        targets = [(w // 2, h // 2)]
    target = min(targets, key=lambda t: (manhattan((sx, sy), t), abs(t[0] - (w - 1)) + abs(t[1] - (h - 1))))

    best = None
    best_key = None
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inside(nx, ny) or (nx, ny) in obstacles:
            nx, ny = sx, sy
        gain = 0
        if (nx, ny) in self_t:
            gain = 0
        elif (nx, ny) in opp_t:
            gain = 2  # flipping opponent-owned cell
        elif (nx, ny) in unclaimed:
            gain = 1  # claiming unclaimed
        else:
            gain = 0  # landing on anything else shouldn't happen often
        # Tie-breakers: prefer moving closer to target; prefer corner-ward sweep consistency
        key = (gain, -manhattan((nx, ny), target), -abs((nx) - (w - 1)) - abs((ny) - (h - 1)))
        if best_key is None or key > best_key:
            best_key = key
            best = [dx, dy]

    if best is None:
        return [0, 0]
    return [int(best[0]), int(best[1])]