def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = map(int, observation.get("self_position", (0, 0)))
    ox, oy = map(int, observation.get("opponent_position", (w - 1, h - 1)))

    def to_set(key):
        s = set()
        for p in observation.get(key) or []:
            if isinstance(p, (list, tuple)) and len(p) >= 2:
                x, y = int(p[0]), int(p[1])
                if 0 <= x < w and 0 <= y < h:
                    s.add((x, y))
        return s

    obstacles = to_set("obstacles")
    resources = to_set("resources")
    unclaimed = to_set("unclaimed_cells")
    opp_terr = to_set("opponent_territory")
    self_terr = to_set("self_territory")

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    t = int(observation.get("turn_index", 0) or 0)

    def ok(nx, ny):
        return 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles

    # Frontier target: prefer claiming cells adjacent to our territory when we're behind,
    # otherwise push into opponent territory.
    behind = int(observation.get("self_territory_count", 0) or 0) < int(observation.get("opponent_territory_count", 0) or 0)
    frontier = set()
    for (x, y) in self_terr:
        for dx, dy in dirs:
            if dx == 0 and dy == 0:
                continue
            nx, ny = x + dx, y + dy
            if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles:
                if (nx, ny) in unclaimed or (nx, ny) in opp_terr:
                    frontier.add((nx, ny))

    best = None
    best_v = -10**18
    for i, (dx, dy) in enumerate(dirs):
        nx, ny = sx + dx, sy + dy
        if not ok(nx, ny):
            nx, ny = sx, sy
            dx, dy = 0, 0

        v = 0.0
        if (nx, ny) in opp_terr:
            v += 9.0
        elif (nx, ny) in unclaimed:
            v += 3.2
        elif (nx, ny) in self_terr:
            v += 0.8
        else:
            v += 0.2

        if (nx, ny) in resources:
            v += 2.0

        # Encourage attacking: move closer to opponent when possible.
        dist_op = abs(nx - ox) + abs(ny - oy)
        v += -0.12 * dist_op

        # Encourage frontier building when behind.
        if behind and frontier:
            d_front = min(abs(nx - fx) + abs(ny - fy) for (fx, fy) in frontier)
            v += -0.18 * d_front
        elif not behind:
            # When ahead, avoid pointless moves; prefer staying near our territory or unclaimed.
            if (nx, ny) not in self_terr and (nx, ny) not in unclaimed:
                v -= 0.9

        # Deterministic tie-break with slight turn-dependent bias.
        v += 0.001 * ((i + t) % 9)

        if v > best_v:
            best_v = v
            best = (dx, dy)

    return [int(best[0]), int(best[1])]