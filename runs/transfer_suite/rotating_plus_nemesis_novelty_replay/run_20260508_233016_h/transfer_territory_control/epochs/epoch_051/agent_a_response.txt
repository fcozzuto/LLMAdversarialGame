def choose_move(observation):
    sx, sy = observation.get("self_position", (0, 0))
    w, h = observation.get("grid_width", 1), observation.get("grid_height", 1)
    ox, oy = observation.get("opponent_position", (sx, sy))
    obstacles = set(tuple(p) for p in (observation.get("obstacles") or []))
    inb = lambda x, y: 0 <= x < w and 0 <= y < h
    man = lambda ax, ay, bx, by: abs(ax - bx) + abs(ay - by)

    self_set = set(tuple(p) for p in (observation.get("self_territory") or []))
    opp_set = set(tuple(p) for p in (observation.get("opponent_territory") or []))
    unclaimed = [tuple(p) for p in (observation.get("unclaimed_cells") or [])]

    # Prefer frontier: unclaimed cells adjacent to our territory, else any unclaimed.
    frontier = []
    if self_set:
        for (tx, ty) in unclaimed:
            for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1), (1, 1), (1, -1), (-1, 1), (-1, -1)):
                if (tx + dx, ty + dy) in self_set:
                    frontier.append((tx, ty))
                    break
    targets = frontier if frontier else unclaimed
    if not targets:
        targets = [((w // 2), (h // 2))]

    cand = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    best = [0, 0]
    best_val = -10**18

    # Limit target scan for speed; deterministic by sorting.
    targets = sorted(set(targets), key=lambda p: (man(sx, sy, p[0], p[1]), p[0], p[1]))[:24]

    for dx, dy in cand:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue

        d_to_target = min(man(nx, ny, tx, ty) for tx, ty in targets)
        d_to_opp = man(nx, ny, ox, oy)

        # Cell value: claim unclaimed > reinforce self > flip opponent.
        cell = (nx, ny)
        if cell in opp_set:
            cell_val = 2600  # flipping helps; also generally moves contest line
        elif cell in self_set:
            cell_val = 1200
        else:
            cell_val = 2000 if cell in set(unclaimed) else 1000

        # Territory control tempo: push toward target but avoid getting swept next.
        # Staying still is allowed; discourage only if it worsens both distance and safety.
        safety = d_to_opp * 180
        progress = -d_to_target * 900

        val = cell_val + safety + progress
        # Small deterministic tie-breaker to reduce oscillation: prefer non-stays.
        if dx == 0 and dy == 0:
            val -= 25

        if val > best_val:
            best_val = val
            best = [dx, dy]

    return best