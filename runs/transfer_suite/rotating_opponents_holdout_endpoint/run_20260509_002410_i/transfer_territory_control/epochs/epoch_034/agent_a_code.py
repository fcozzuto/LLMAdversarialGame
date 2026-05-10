def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", (0, 0))
    obstacles = set(map(tuple, observation.get("obstacles") or []))
    unclaimed = set(map(tuple, observation.get("unclaimed_cells") or []))
    opp_t = set(map(tuple, observation.get("opponent_territory") or []))
    resources = observation.get("resources") or []

    def inside(x, y): return 0 <= x < w and 0 <= y < h
    def neighbors8(x, y):
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                if dx != 0 or dy != 0:
                    nx, ny = x + dx, y + dy
                    if inside(nx, ny):
                        yield nx, ny

    if not inside(sx, sy):
        sx, sy = 0, 0

    frontier = set()
    for x, y in opp_t:
        for nx, ny in neighbors8(x, y):
            if (nx, ny) in unclaimed and (nx, ny) not in obstacles:
                frontier.add((nx, ny))

    # Resource bias if present (typically none per spec, but keep safe)
    res_set = set(map(tuple, resources or []))
    target = None
    if frontier:
        target = sorted(frontier, key=lambda c: (abs(c[0]-sx)+abs(c[1]-sy), c[0], c[1]))[0]
    elif res_set:
        cand = [c for c in res_set if c not in obstacles and inside(c[0], c[1])]
        if cand:
            target = sorted(cand, key=lambda c: (abs(c[0]-sx)+abs(c[1]-sy), c[0], c[1]))[0]
    else:
        all_unclaimed = [c for c in unclaimed if c not in obstacles and inside(c[0], c[1])]
        if all_unclaimed:
            # Prefer toward center to reduce giving opponent expansion lanes
            cx, cy = (w - 1) / 2.0, (h - 1) / 2.0
            target = sorted(all_unclaimed, key=lambda c: (abs(c[0]-sx)+abs(c[1]-sy), abs(c[0]-cx)+abs(c[1]-cy), c[0], c[1]))[0]

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best = (10**9, 10**9, 0, 0)
    best_move = (0, 0)

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if (nx, ny) in obstacles or not inside(nx, ny):
            continue
        # If target exists, move greedily; otherwise expand toward unclaimed/opp territory boundaries.
        if target is not None:
            dist = abs(target[0]-nx) + abs(target[1]-ny)
        else:
            dist = 0
            # Prefer stepping adjacent to opponent territory or into unclaimed cells
            if (nx, ny) in unclaimed:
                dist -= 5
            if (nx, ny) in opp_t:
                dist -= 2
            adj_opp = 0
            for ax, ay in neighbors8(nx, ny):
                if (ax, ay) in opp_t:
                    adj_opp += 1
            dist += -3 * adj_opp

        # Extra preference: avoid oscillations by slight penalty for repeating direction patterns
        # (deterministic, no history used)
        center_bias = abs(nx - (w - 1) / 2.0) + abs(ny - (h - 1) / 2.0)

        # If flipping is on, stepping into opponent territory can be beneficial; prioritize it.
        flip_bonus = -8 if (nx, ny) in opp_t else 0
        claim_bonus = -6 if (nx, ny) in unclaimed else 0

        score = dist + 0.1 * center_bias + flip_bonus + claim_bonus
        # Deterministic tie-break
        key = (int(score * 1000), abs(dx) + abs(dy), dx, dy)
        if key < best:
            best = key
            best_move = (dx, dy)

    dx, dy = best_move
    return [int(dx), int(dy)]