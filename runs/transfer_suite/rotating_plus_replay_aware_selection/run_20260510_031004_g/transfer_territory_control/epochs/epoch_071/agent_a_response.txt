def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation.get("self_position", (0, 0))
    obstacles = set(map(tuple, observation.get("obstacles", []) or []))
    unclaimed = set(map(tuple, observation.get("unclaimed_cells", []) or []))
    opp_terr = set(map(tuple, observation.get("opponent_territory", []) or []))
    self_terr = set(map(tuple, observation.get("self_territory", []) or []))
    cx, cy = (w - 1) / 2.0, (h - 1) / 2.0

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    adj_opp = set()
    for x, y in opp_terr:
        for dx, dy in dirs:
            nx, ny = x + dx, y + dy
            if inb(nx, ny) and (nx, ny) not in obstacles:
                adj_opp.add((nx, ny))

    def center_dist(x, y):
        return abs(x - cx) + abs(y - cy)

    best = None
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue
        val = 0
        if (nx, ny) in opp_terr:
            val += 40
        elif (nx, ny) in unclaimed:
            val += 22
        elif (nx, ny) in self_terr:
            val += 2
        if (nx, ny) in adj_opp:
            val += 12
        # Prefer expanding toward center, but keep some pressure toward opponent
        distc = center_dist(nx, ny)
        disto = abs(nx - observation.get("opponent_position", (w - 1, h - 1))[0]) + abs(ny - observation.get("opponent_position", (w - 1, h - 1))[1])
        score = val * 100 - int(distc * 3 + disto)
        if best is None or score > best[0] or (score == best[0] and (dx, dy) < best[1]):
            best = (score, (dx, dy))

    if best is None:
        return [0, 0]
    return [int(best[1][0]), int(best[1][1])]