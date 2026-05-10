def choose_move(observation):
    w = int(observation["grid_width"])
    h = int(observation["grid_height"])
    sx, sy = observation["self_position"]
    obstacles = set(tuple(p) for p in (observation.get("obstacles") or []))
    self_terr = set(tuple(p) for p in (observation.get("self_territory") or []))
    opp_terr = set(tuple(p) for p in (observation.get("opponent_territory") or []))
    unclaimed = set(tuple(p) for p in (observation.get("unclaimed_cells") or []))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    ti = int(observation.get("turn_index", 0)) % 9
    dirs = dirs[ti:] + dirs[:ti]

    # Frontier: unclaimed cells adjacent to our territory
    frontier = set()
    if self_terr:
        for x, y in self_terr:
            for dx, dy in dirs:
                nx, ny = x + dx, y + dy
                if inb(nx, ny) and (nx, ny) in unclaimed:
                    frontier.add((nx, ny))
    targets = frontier if frontier else unclaimed if unclaimed else opp_terr

    def md(cells, x, y):
        best = 10**9
        for px, py in cells:
            d = abs(px - x) + abs(py - y)
            if d < best:
                best = d
        return best if best != 10**9 else 0

    d_to_un = md(targets, sx, sy)
    d_to_opp = md(opp_terr, sx, sy) if opp_terr else 99

    best_mv = (0, 0)
    best_sc = -10**18
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue

        if (nx, ny) in self_terr:
            base = 0.4
        elif (nx, ny) in unclaimed:
            base = 2.4
        elif (nx, ny) in opp_terr:
            base = 2.0
        else:
            base = 0.2

        sc = base
        if targets:
            sc += -0.06 * (abs(nx - next(iter(targets))[0]) + abs(ny - next(iter(targets))[1]))  # cheap, deterministic tie-breaker
            sc += -0.02 * (abs(d_to_un))  # keep overall heading consistent
        sc += -0.03 * d_to_opp  # prefer reducing distance to capture/contests
        sc += 0.01 * (1 if (nx, ny) in frontier else 0)

        if sc > best_sc or (sc == best_sc and (dx, dy) < best_mv):
            best_sc = sc
            best_mv = (dx, dy)

    return [int(best_mv[0]), int(best_mv[1])]