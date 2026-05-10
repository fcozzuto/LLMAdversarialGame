def choose_move(observation):
    w = int(observation["grid_width"])
    h = int(observation["grid_height"])
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    obstacles = set(tuple(p) for p in (observation.get("obstacles") or []))
    self_terr = set(tuple(p) for p in (observation.get("self_territory") or []))
    opp_terr = set(tuple(p) for p in (observation.get("opponent_territory") or []))
    unclaimed = list(observation.get("unclaimed_cells") or [])

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    t = int(observation.get("turn_index", 0))
    dirs = dirs[t % 9:] + dirs[:t % 9]

    def inside(x, y):
        return 0 <= x < w and 0 <= y < h

    def man(a, b, c, d):
        return abs(a - c) + abs(b - d)

    opp_front = set()
    for (x, y) in opp_terr:
        for dx, dy in dirs:
            nx, ny = x + dx, y + dy
            if inside(nx, ny) and (nx, ny) not in opp_terr and (nx, ny) not in obstacles:
                opp_front.add((nx, ny))

    targets = unclaimed[:]
    if not targets:
        targets = list(opp_front) if opp_front else []
    if not targets:
        targets = list(opp_front) + unclaimed

    best = (0, 0, (-0), 0)
    # best = (primary, secondary, tie, move)
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inside(nx, ny) or (nx, ny) in obstacles:
            continue
        primary = 0
        secondary = 0
        if (nx, ny) in self_terr:
            primary += 1
        elif (nx, ny) in opp_terr:
            primary += 30
            secondary += man(ox, oy, nx, ny)
        elif (nx, ny) in unclaimed or (nx, ny) not in self_terr and (nx, ny) not in opp_terr:
            primary += 60
        else:
            primary += 5

        # push toward best available target
        if targets:
            d_to_best = min(man(nx, ny, p[0], p[1]) for p in targets)
            primary += 50 - 2 * d_to_best
            secondary += d_to_best

        # mild pressure: reduce distance to opponent when attacking frontier
        if (nx, ny) in opp_front:
            secondary -= 1

        # deterministic tie-breaking: prefer center-ish and lexicographic dirs
        center = man(nx, ny, (w - 1) // 2, (h - 1) // 2)
        secondary += center // 2

        key = (primary, -secondary, 0)
        if best[0] == 0 and best[3] == 0 and key == (0, -0, 0):
            pass
        if primary > best[0] or (primary == best[0] and (-secondary) > best[1]):
            best = (primary, -secondary, 0, (dx, dy))

    dx, dy = best[3] if best[3] != 0 else (0, 0)
    return [int(dx), int(dy)]