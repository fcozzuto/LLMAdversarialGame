def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position", [0, 0]) or [0, 0]
    op = observation.get("opponent_position", [0, 0]) or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for o in observation.get("obstacles", []) or []:
        if isinstance(o, (list, tuple)) and len(o) >= 2:
            obstacles.add((int(o[0]), int(o[1])))

    resources = []
    for r in observation.get("resources", []) or []:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            rx, ry = int(r[0]), int(r[1])
            if (rx, ry) not in obstacles:
                resources.append((rx, ry))
    if not resources:
        return [0, 0]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def step_block_pen(x, y):
        if (x, y) in obstacles:
            return 10**9
        p = 0
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                if dx == 0 and dy == 0:
                    continue
                if (x + dx, y + dy) in obstacles:
                    p += 2
        return p

    moves = [(dx, dy) for dx in (-1, 0, 1) for dy in (-1, 0, 1)]
    best = None
    best_score = -10**18

    # Precompute top candidate resources deterministically: favor corners/edges farther from center
    cx, cy = (w - 1) / 2.0, (h - 1) / 2.0
    res_sorted = sorted(resources, key=lambda r: (-(abs(r[0] - cx) + abs(r[1] - cy)), r[0], r[1]))
    candidates = res_sorted[: min(6, len(res_sorted))]

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            sc = -10**18
        else:
            sc = -step_block_pen(nx, ny)
            # Evaluate only a small contested set for robustness
            for rx, ry in candidates:
                if (rx, ry) in obstacles:
                    continue
                sd = abs(rx - nx) + abs(ry - ny)
                od = abs(rx - ox) + abs(ry - oy)
                # Strongly prefer winning races; if tied, prefer closer-for-us
                race = (od - sd)
                sc += (race * 10) + (2 if sd == 0 else 0)
                # If opponent is much closer, consider intercept: move to reduce our distance to that resource
                if od - sd > -1:
                    sc += max(0, 6 - sd)
                else:
                    sc -= min(6, sd)
            # Add slight preference for moving toward resources when unsure
            if candidates:
                tr = candidates[0]
                sc += - (abs(tr[0] - nx) + abs(tr[1] - ny)) * 0.01
        if sc > best_score or (sc == best_score and (dx, dy) < best):
            best_score = sc
            best = (dx, dy)

    return [int(best[0]), int(best[1])]