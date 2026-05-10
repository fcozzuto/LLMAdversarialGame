def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", (0, 0))
    sx, sy = int(sx), int(sy)

    obs = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obs.add((x, y))

    opp_terr = set()
    for c in observation.get("opponent_territory") or []:
        if isinstance(c, (list, tuple)) and len(c) >= 2:
            x, y = int(c[0]), int(c[1])
            if 0 <= x < w and 0 <= y < h:
                opp_terr.add((x, y))

    unclaimed = set()
    for c in observation.get("unclaimed_cells") or []:
        if isinstance(c, (list, tuple)) and len(c) >= 2:
            x, y = int(c[0]), int(c[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obs:
                unclaimed.add((x, y))

    def cheb(a, b):
        return max(abs(a[0] - b[0]), abs(a[1] - b[1]))

    neigh = [(dx, dy) for dx in (-1, 0, 1) for dy in (-1, 0, 1) if not (dx == 0 and dy == 0)]
    moves = [(0, 0)] + neigh

    # Prefer unclaimed cells adjacent to opponent territory to intercept/flip.
    frontier = []
    for (x, y) in unclaimed:
        hit = False
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                if dx == 0 and dy == 0:
                    continue
                if (x + dx, y + dy) in opp_terr:
                    hit = True
                    break
            if hit:
                break
        if hit:
            frontier.append((x, y))

    targets = frontier if frontier else list(unclaimed)
    if not targets:
        # Fallback: go after opponent territory directly (entering flips).
        targets = list(opp_terr)

    # If still empty, stay.
    if not targets:
        return [0, 0]

    # Choose a deterministic target: minimum cheb distance from us, then lexicographic.
    target = min(targets, key=lambda t: (cheb((sx, sy), t), t[0], t[1]))

    best = (-10**9, 0, 0)
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h) or (nx, ny) in obs:
            continue

        cell = (nx, ny)
        if cell in opp_terr:
            base = 10
        elif cell in unclaimed:
            base = 4
        else:
            base = 1  # own territory or other
        prog = -cheb(cell, target)

        # Small extra to avoid drifting away from the target.
        if dx == 0 and dy == 0:
            base -= 1

        sc = base * 3 + prog
        if sc > best[0] or (sc == best[0] and (dx, dy) < (best[1], best[2])):
            best = (sc, dx, dy)

    return [int(best[1]), int(best[2])]