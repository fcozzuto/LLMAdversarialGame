def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))

    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))
    self_terr = set(tuple(p) for p in (observation.get("self_territory", []) or []))
    opp_terr = set(tuple(p) for p in (observation.get("opponent_territory", []) or []))
    unclaimed = set(tuple(p) for p in (observation.get("unclaimed_cells", []) or []))
    resources = set(tuple(p) for p in (observation.get("resources", []) or []))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    dirs = [(-1, 0), (1, 0), (0, -1), (0, 1), (-1, -1), (-1, 1), (1, -1), (1, 1), (0, 0)]

    def md(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    targets = []
    # Prioritize reclaiming opponent territory (counterclaim opponent archetype)
    if opp_terr:
        targets.extend(list(opp_terr))
    # Then take unclaimed cells that help expansion
    if unclaimed:
        targets.extend(list(unclaimed))
    # Then resources if any (rare; deterministic fallback)
    if resources:
        targets.extend(list(resources))

    if not targets:
        # No known targets: try to stay safe inside our territory or move toward center
        cx, cy = (w - 1) / 2.0, (h - 1) / 2.0
        best = (0, 0)
        bestv = None
        for dx, dy in dirs:
            nx, ny = sx + dx, sy + dy
            if not inb(nx, ny) or (nx, ny) in obstacles:
                continue
            v = (0 if (nx, ny) in self_terr else 1) + md((nx, ny), (cx, cy))
            if bestv is None or v < bestv:
                bestv = v
                best = (dx, dy)
        return [best[0], best[1]]

    # Precompute closest target distances for current and new positions (greedy)
    # Using simple min over targets is fine for 8x8.
    best_move = (0, 0)
    best_val = None

    center_bias = 0.15
    opp_bias = 0.08
    step_order = {d: i for i, d in enumerate(dirs)}  # deterministic tie-break

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue

        v = 0.0

        # Territory control priorities
        if (nx, ny) in opp_terr:
            v += 80.0
        if (nx, ny) in unclaimed:
            v += 25.0
        if (nx, ny) in self_terr:
            v += 12.0

        # If moving reduces distance to the nearest target, reward it
        cur_td = min(md((sx, sy), t) for t in targets)
        new_td = min(md((nx, ny), t) for t in targets)
        v += (cur_td - new_td) * 6.0

        # Small bias toward center and away from opponent position (territory_counterclaim)
        cx, cy = (w - 1) / 2.0, (h - 1) / 2.0
        v += -center_bias * md((nx, ny), (cx, cy))
        v += opp_bias * md((nx, ny), (ox, oy))

        # Deterministic tie-break: prefer lower index in dirs
        if best_val is None or v > best_val + 1e-9 or (abs(v - best_val) <= 1e-9 and step_order[(dx, dy)] < step_order[best_move]):
            best_val = v
            best_move = (dx, dy)

    # Fallback: should never happen due to dirs including (0,0)
    return [int(best_move[0]), int(best_move[1])]