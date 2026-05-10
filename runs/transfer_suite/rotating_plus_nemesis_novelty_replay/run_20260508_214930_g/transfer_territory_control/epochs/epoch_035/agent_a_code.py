def choose_move(observation):
    w, h = observation["grid_width"], observation["grid_height"]
    sx, sy = observation["self_position"]
    opp_t = set(map(tuple, observation.get("opponent_territory") or []))
    self_t = set(map(tuple, observation.get("self_territory") or []))
    obstacles = set(map(tuple, observation.get("obstacles") or []))
    unclaimed = set(map(tuple, observation.get("unclaimed_cells") or []))

    def inb(x, y): return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles
    def adj_cells(x, y):
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                if dx or dy: yield (x + dx, y + dy)
    def man(a, b): return abs(a[0] - b[0]) + abs(a[1] - b[1])

    opp_front = set()
    for (x, y) in opp_t:
        for nx, ny in adj_cells(x, y):
            if 0 <= nx < w and 0 <= ny < h and (nx, ny) in unclaimed:
                opp_front.add((nx, ny))
    targets = list(opp_front) if opp_front else list(unclaimed) if unclaimed else list(opp_t)
    if not targets:
        return [0, 0]
    opp_pos = tuple(observation["opponent_position"])

    def cell_value(x, y):
        if (x, y) in obstacles: return -10**9
        val = 0
        if (x, y) in opp_t:
            val += 8
        elif (x, y) in unclaimed:
            val += 3
        elif (x, y) in self_t:
            val += 1
        # Expand toward contested space: prefer moving into cells adjacent to opponent territory
        adj_opp = any((nx, ny) in opp_t for nx, ny in adj_cells(x, y) if 0 <= nx < w and 0 <= ny < h)
        if adj_opp:
            val += 2
        # Keep some pressure: prefer closeness to nearest target in frontier/unclaimed
        d = min(man((x, y), t) for t in targets)
        val += max(0, 4 - d) * 1.0
        # Avoid stepping too close to opponent position unless it also contests
        dop = man((x, y), opp_pos)
        if dop <= 1 and (x, y) not in opp_t:
            val -= 2
        return val

    best = (0, 0, -10**18)
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            if not inb(nx, ny): continue
            v = cell_value(nx, ny)
            if v > best[2]:
                best = (dx, dy, v)
            # deterministic tie-break: favor smaller dx then smaller dy then staying
            elif v == best[2]:
                if (dx, dy) < (best[0], best[1]):
                    best = (dx, dy, v)
    return [int(best[0]), int(best[1])]