def choose_move(observation):
    w = int(observation["grid_width"])
    h = int(observation["grid_height"])
    x, y = observation["self_position"]
    ox, oy = observation["opponent_position"]
    selfT = set(tuple(p) for p in (observation.get("self_territory") or []))
    oppT = set(tuple(p) for p in (observation.get("opponent_territory") or []))
    unclaimed = set(tuple(p) for p in (observation.get("unclaimed_cells") or []))
    obstacles = set(tuple(p) for p in (observation.get("obstacles") or []))

    def inb(nx, ny):
        return 0 <= nx < w and 0 <= ny < h

    def man(a, b, c, d):
        v = a - c
        if v < 0:
            v = -v
        u = b - d
        if u < 0:
            u = -u
        return v + u

    # Bias toward opponent's side while prioritizing captures and safe frontier expansion.
    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best = None
    best_score = None

    # Precompute nearest edge-unclaimed as a deterministic pressure target.
    edge_unclaimed = [p for p in unclaimed if p[0] in (0, w - 1) or p[1] in (0, h - 1)]
    if edge_unclaimed:
        tx, ty = min(edge_unclaimed, key=lambda p: (man(x, y, p[0], p[1]), p[0], p[1]))
    else:
        tx, ty = (ox, oy)

    for dx, dy in dirs:
        nx, ny = x + dx, y + dy
        if not inb(nx, ny):
            continue
        if (nx, ny) in obstacles:
            score = -10_000
        else:
            score = 0
            if (nx, ny) in oppT:
                score += 200  # strong incentive to flip opponent territory
            elif (nx, ny) in unclaimed:
                score += 40   # expanding into unclaimed
            elif (nx, ny) in selfT:
                score += 6    # avoid wasting moves
            # Frontier pressure: move toward opponent generally
            score += -2 * man(nx, ny, ox, oy)
            # Also contest edge targets deterministically (opponent archetype suggests edge play)
            score += -man(nx, ny, tx, ty)
            # Mild preference to avoid stepping away from any unclaimed cell if possible
            if unclaimed:
                dmin = min(manhattan for manhattan in [man(nx, ny, p[0], p[1]) for p in unclaimed if p]) if unclaimed else 0
                score += -0.05 * dmin

        if best_score is None or score > best_score:
            best_score = score
            best = [dx, dy]

    return best if best is not None else [0, 0]