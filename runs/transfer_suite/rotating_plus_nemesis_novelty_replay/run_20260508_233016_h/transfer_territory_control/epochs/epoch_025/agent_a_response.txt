def choose_move(observation):
    sx, sy = observation["self_position"]
    w, h = observation["grid_width"], observation["grid_height"]
    obstacles = set(tuple(p) for p in (observation.get("obstacles") or []))
    self_terr = set(tuple(p) for p in (observation.get("self_territory") or []))
    opp_terr = set(tuple(p) for p in (observation.get("opponent_territory") or []))
    unclaimed = set(tuple(p) for p in (observation.get("unclaimed_cells") or []))

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def man(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    # Prefer unclaimed adjacent to our territory to expand territory safely.
    adj_candidates = []
    for (x, y) in self_terr:
        for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1), (-1, -1), (-1, 1), (1, -1), (1, 1)]:
            c = (x + dx, y + dy)
            if c in unclaimed:
                adj_candidates.append(c)

    targets = adj_candidates if adj_candidates else list(unclaimed)
    if not targets:
        # If no unclaimed, either grab opponent territory or drift toward center.
        targets = list(opp_terr)
        if not targets:
            targets = [(w // 2, h // 2)]

    target = min(targets, key=lambda c: man((sx, sy), c))

    best = None
    best_val = -10**18
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            nx, ny, dx, dy = sx, sy, 0, 0
        cell = (nx, ny)

        val = 0.0
        if cell in self_terr:
            val += 0.2
        if cell in unclaimed:
            val += 2.5
        if cell in opp_terr:
            val += 1.8  # likely flips on entry, gaining directly contested cells

        # Drive toward target; strongly encourage reducing distance.
        d_old = man((sx, sy), target)
        d_new = man(cell, target)
        val += (d_old - d_new) * 0.9

        # Small center bias to avoid getting stuck on edges.
        cx, cy = (w - 1) / 2.0, (h - 1) / 2.0
        val += -0.01 * (abs(nx - cx) + abs(ny - cy))

        # Deterministic tie-break.
        cand = (val, dx, dy, nx, ny)
        if best is None or cand > best:
            best = cand
            best_val = val

    return [best[1], best[2]]