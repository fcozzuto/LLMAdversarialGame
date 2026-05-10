def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sx, sy = map(int, observation.get("self_position") or [0, 0])
    ox, oy = map(int, observation.get("opponent_position") or [w - 1, h - 1])

    obs_cells = set()
    for p in (observation.get("obstacles") or []):
        if p and len(p) >= 2:
            obs_cells.add((int(p[0]), int(p[1])))

    unclaimed = set((int(x), int(y)) for x, y in (observation.get("unclaimed_cells") or []))
    my_terr = set((int(x), int(y)) for x, y in (observation.get("self_territory") or []))
    their_terr = set((int(x), int(y)) for x, y in (observation.get("opponent_territory") or []))

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    # Prefer unclaimed cells adjacent to opponent territory (edge pressure).
    adj_to_their = set()
    for (tx, ty) in their_terr:
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                if dx == 0 and dy == 0:
                    continue
                nx, ny = tx + dx, ty + dy
                if inb(nx, ny) and (nx, ny) in unclaimed:
                    adj_to_their.add((nx, ny))
    targets = adj_to_their if adj_to_their else unclaimed

    def cell_value(x, y):
        if (x, y) in their_terr:
            return 2.0  # flipping on entry
        if (x, y) in unclaimed:
            return 1.0
        if (x, y) in my_terr:
            return 0.0
        return 0.0

    best = (-(10**9), 0, 0)
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        if (nx, ny) in obs_cells:
            nx, ny = sx, sy  # deterministic evaluation of rejected move as stay
        score = 0.0
        score += cell_value(nx, ny)

        # Progress toward target set: closest target to opponent, but tie-break by closeness to us.
        if targets:
            t = min(targets, key=lambda p: (abs(p[0] - ox) + abs(p[1] - oy), abs(p[0] - sx) + abs(p[1] - sy)))
            score += - (abs(nx - t[0]) + abs(ny - t[1])) * 0.03

        # Also slightly prefer moving toward opponent to enable edge trades.
        score += - (abs(nx - ox) + abs(ny - oy)) * 0.01

        # Discourage staying if there is an improving move.
        if dx == 0 and dy == 0:
            score -= 0.02

        # Deterministic tie-break: prefer smallest dx then dy.
        cand = (score, -dx, -dy)
        if cand > best:
            best = cand

    _, ndx, ndy = best
    return [-ndx, -ndy]