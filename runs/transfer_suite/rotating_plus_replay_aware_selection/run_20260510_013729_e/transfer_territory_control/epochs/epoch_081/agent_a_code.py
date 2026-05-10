def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    x, y = observation.get("self_position") or [0, 0]
    x, y = int(x), int(y)

    self_t = observation.get("self_territory") or []
    opp_t = observation.get("opponent_territory") or []
    obs_list = observation.get("obstacles") or []
    unclaimed = observation.get("unclaimed_cells") or []

    self_set = set((int(p[0]), int(p[1])) for p in self_t if isinstance(p, (list, tuple)) and len(p) >= 2)
    opp_set = set((int(p[0]), int(p[1])) for p in opp_t if isinstance(p, (list, tuple)) and len(p) >= 2)
    blocked = set((int(p[0]), int(p[1])) for p in obs_list if isinstance(p, (list, tuple)) and len(p) >= 2)
    un_set = set((int(p[0]), int(p[1])) for p in unclaimed if isinstance(p, (list, tuple)) and len(p) >= 2)

    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    frontier = set()
    for (sx, sy) in self_set:
        for dx, dy in dirs:
            nx, ny = sx + dx, sy + dy
            if 0 <= nx < w and 0 <= ny < h and (nx, ny) in un_set and (nx, ny) not in blocked:
                frontier.add((nx, ny))
    if not frontier:
        frontier = un_set

    # Pick a single deterministic target cell.
    if frontier:
        tx, ty = min(frontier, key=lambda c: (abs(c[0] - x) + abs(c[1] - y), c[0], c[1]))
    else:
        # If nothing else, head toward opponent (aggressive flip).
        if opp_set:
            tx, ty = min(opp_set, key=lambda c: (abs(c[0] - x) + abs(c[1] - y), c[0], c[1]))
        else:
            tx, ty = x, y

    def neighbor_count(nx, ny):
        c = 0
        for dx, dy in dirs:
            ax, ay = nx + dx, ny + dy
            if 0 <= ax < w and 0 <= ay < h:
                if (ax, ay) in un_set:
                    c += 1
        return c

    best = None
    best_val = -10**18
    for dx, dy in dirs:
        nx, ny = x + dx, y + dy
        if not (0 <= nx < w and 0 <= ny < h):
            continue
        if (nx, ny) in blocked:
            continue

        # Immediate gain
        if (nx, ny) in opp_set:
            base = 7
        elif (nx, ny) in un_set:
            base = 4
        elif (nx, ny) in self_set:
            base = 1
        else:
            base = 0  # should be rare

        # Strategic shaping: move toward target, but reward stepping onto expansion frontiers.
        dist = abs(nx - tx) + abs(ny - ty)
        val = base * 100 - dist * 3 + neighbor_count(nx, ny) * 2

        # Small deterministic tie-break to reduce jitter
        val += (0.001 * (nx * 0.37 + ny * 0.19))

        if val > best_val:
            best_val = val
            best = (dx, dy)

    if best is None:
        return [0, 0]
    return [int(best[0]), int(best[1])]