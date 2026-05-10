def choose_move(observation):
    W = int(observation.get("grid_width", 8) or 8)
    H = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])

    def to_set(v):
        s = set()
        for p in v or []:
            if p and len(p) >= 2:
                x, y = int(p[0]), int(p[1])
                if 0 <= x < W and 0 <= y < H:
                    s.add((x, y))
        return s

    obstacles = to_set(observation.get("obstacles"))
    resources = to_set(observation.get("resources"))
    unclaimed = to_set(observation.get("unclaimed_cells"))
    self_t = to_set(observation.get("self_territory"))
    opp_t = to_set(observation.get("opponent_territory"))

    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    def inb(x, y): return 0 <= x < W and 0 <= y < H
    def man(x1, y1, x2, y2): return abs(x1 - x2) + abs(y1 - y2)

    # Prefer contesting opponent frontier: opponent cells adjacent to unclaimed.
    opp_frontier = set()
    for (x, y) in opp_t:
        for dx, dy in dirs:
            nx, ny = x + dx, y + dy
            if inb(nx, ny) and (nx, ny) in unclaimed:
                opp_frontier.add((x, y))
                break

    # If no frontier, fall back to unclaimed boundary near our side.
    targets = opp_frontier if opp_frontier else unclaimed
    if resources:
        # If we have resources, bias toward their locations deterministically.
        targets = resources | (opp_frontier if opp_frontier else unclaimed)

    if not targets:
        return [0, 0]

    # Deterministic target: closest to us (tie-breaker: smallest coordinates).
    tx, ty = min(targets, key=lambda t: (man(sx, sy, t[0], t[1]), t[0], t[1]))

    best = None
    best_val = -10**18
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            nx, ny = sx, sy  # engine keeps us in place
            dx, dy = 0, 0

        val = 0
        if (nx, ny) in opp_t:
            val += 6  # stealing/contesting
        if (nx, ny) in unclaimed:
            val += 3  # immediate expansion
        if (nx, ny) in self_t:
            val += 1  # consolidation
        # Move toward the chosen frontier target
        val += 2 * (-man(nx, ny, tx, ty))

        # Discourage getting boxed in / stepping near obstacles
        adj_obs = 0
        for ddx, ddy in dirs:
            ax, ay = nx + ddx, ny + ddy
            if inb(ax, ay) and (ax, ay) in obstacles:
                adj_obs += 1
        val -= 0.6 * adj_obs

        # Deterministic tie-break
        key = (val, -nx, -ny, dx, dy)
        if best is None or key > best_val:
            best_val = key
            best = [dx, dy]

    return best if best is not None else [0, 0]