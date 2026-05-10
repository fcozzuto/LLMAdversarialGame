def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [7, 7])

    obstacles = set(tuple(p) for p in (observation.get("obstacles") or []))
    self_t = set(tuple(p) for p in (observation.get("self_territory") or []))
    opp_t = set(tuple(p) for p in (observation.get("opponent_territory") or []))
    unclaimed = set(tuple(p) for p in (observation.get("unclaimed_cells") or []))

    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def man(a, b, c, d):
        return abs(a - c) + abs(b - d)

    opp_neighbors = set()
    for (x, y) in opp_t:
        for dx, dy in dirs:
            nx, ny = x + dx, y + dy
            if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles:
                if (nx, ny) in unclaimed:
                    opp_neighbors.add((nx, ny))

    # Pick deterministic target bias: nearest opp-border unclaimed, else nearest global unclaimed
    def best_target(cands):
        if not cands:
            return None
        return min(cands, key=lambda t: (man(sx, sy, t[0], t[1]), t[1], t[0]))

    target1 = best_target(opp_neighbors)
    target2 = best_target(unclaimed)

    # Also prefer expanding near our own territory
    adj_self = set()
    for (x, y) in self_t:
        for dx, dy in dirs:
            nx, ny = x + dx, y + dy
            if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles:
                if (nx, ny) not in self_t:
                    adj_self.add((nx, ny))

    best = (0, 0)
    best_sc = -10**18
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue

        sc = 0
        if (nx, ny) in opp_t:
            sc += 2600  # strong flip when possible
        elif (nx, ny) in unclaimed:
            sc += 180
        elif (nx, ny) in self_t:
            sc += 15

        # Attraction to frontier targets
        if target1 is not None:
            sc += 6 * (man(sx, sy, target1[0], target1[1]) - man(nx, ny, target1[0], target1[1]))
        if target2 is not None:
            sc += 3 * (man(sx, sy, target2[0], target2[1]) - man(nx, ny, target2[0], target2[1]))

        # Prefer moves that increase "pressure" near our boundary
        if (nx, ny) in adj_self:
            sc += 25
        # Avoid stepping into opponent too far from goals (keeps deterministic claimer behavior)
        sc -= 0.5 * man(nx, ny, ox, oy)

        # Small deterministic tie-break favoring staying if very close equivalence
        sc += (0.01 if (dx == 0 and dy == 0) else 0)

        if sc > best_sc:
            best_sc = sc
            best = (dx, dy)

    return [int(best[0]), int(best[1])]