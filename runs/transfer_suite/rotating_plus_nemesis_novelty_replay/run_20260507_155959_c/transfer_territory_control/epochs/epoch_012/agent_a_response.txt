def choose_move(observation):
    w = observation.get("grid_width", 8) or 8
    h = observation.get("grid_height", 8) or 8
    sx, sy = (observation.get("self_position", [0, 0]) + [0, 0])[:2]
    cx, cy = w // 2, h // 2

    obstacles = set()
    for p in observation.get("obstacles", []) or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obstacles.add((p[0], p[1]))

    inb = lambda x, y: 0 <= x < w and 0 <= y < h

    self_cells = set(tuple(xy) for xy in (observation.get("self_territory", []) or []))
    opp_cells = set(tuple(xy) for xy in (observation.get("opponent_territory", []) or []))
    unclaimed = [tuple(xy) for xy in (observation.get("unclaimed_cells", []) or [])]

    target = None
    if unclaimed:
        # Prefer unclaimed near center; tie-break by closeness to us.
        best = None
        for x, y in unclaimed:
            if not inb(x, y) or (x, y) in obstacles:
                continue
            score = (abs(x - cx) + abs(y - cy)) * 3 + (abs(x - sx) + abs(y - sy))
            if best is None or score < best[0]:
                best = (score, x, y)
        if best is not None:
            target = (best[1], best[2])
    if target is None:
        target = (cx, cy)

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    def neighbors_free_count(x, y):
        cnt = 0
        for dx, dy in deltas:
            nx, ny = x + dx, y + dy
            if inb(nx, ny) and (nx, ny) not in obstacles:
                cnt += 1
        return cnt

    best_move = (0, 0)
    best_val = -10**18
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        if (nx, ny) in obstacles:
            continue

        if (nx, ny) in self_cells:
            base = 1
        elif (nx, ny) in opp_cells:
            base = 6  # likely flip on entry
        else:
            base = 5  # unclaimed
        d_to_target = abs(nx - target[0]) + abs(ny - target[1])

        # Mild boundary pressure: slightly prefer moves that bring us nearer to opponent territory.
        d_to_opp = 0
        if opp_cells:
            ox, oy = next(iter(opp_cells))
            ox = sum(x for x, _ in opp_cells) // len(opp_cells)
            oy = sum(y for _, y in opp_cells) // len(opp_cells)
            d_to_opp = abs(nx - ox) + abs(ny - oy)

        val = base * 10 - d_to_target * 2 + neighbors_free_count(nx, ny) - d_to_opp * 0.3
        if val > best_val:
            best_val = val
            best_move = (dx, dy)

    return [best_move[0], best_move[1]]