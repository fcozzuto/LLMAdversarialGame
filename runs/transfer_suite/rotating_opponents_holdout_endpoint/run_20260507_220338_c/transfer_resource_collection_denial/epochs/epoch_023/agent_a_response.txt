def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", []) or []
    obstacles = set((p[0], p[1]) for p in (observation.get("obstacles", []) or []))

    if not resources:
        return [0, 0]

    moves = [(-1, -1), (-1, 0), (-1, 1),
             (0, -1), (0, 0), (0, 1),
             (1, -1), (1, 0), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def md(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0:
            dx = -dx
        dy = y1 - y2
        if dy < 0:
            dy = -dy
        return dx + dy

    # Opponent sweep_rows: when they are ahead on a row, prefer resources that keep us closer there,
    # but also bias toward breaking their progress by increasing our distance to them if equal.
    best = None
    best_key = None
    myd0_opp = md(sx, sy, ox, oy)

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue

        # Evaluate immediate contest over all resources
        # - lead: opd - myd (bigger is better)
        # - reward landing on a resource strongly
        # - discourage giving opponent a strictly better lane by moving closer to their position when ties
        score = 0
        for rx, ry in resources:
            myd = md(nx, ny, rx, ry)
            opd = md(ox, oy, rx, ry)
            if (nx, ny) == (rx, ry):
                lead = 10_000 - myd
            else:
                lead = (opd - myd)
                if opd < myd:
                    lead -= 2  # avoid losing races
            # Extra bias: if opponent is on same row as resource, prioritize taking it or contesting it
            if oy == ry:
                if rx == nx:
                    lead += 2
                if ry == ny:
                    lead += 1
            score += lead

        # Distance tie-break: if sums are close, keep away from opponent (break their sweep)
        dist_now = md(nx, ny, ox, oy)
        score2 = score + (dist_now - myd0_opp) * 0.5

        # Deterministic key: (primary score2, then prefer closer to best resource, then lexicographic move)
        if best_key is None or (score2, -abs(nx - w // 2) - abs(ny - h // 2), -dist_now, dx, dy) > best_key:
            best_key = (score2, -abs(nx - w // 2) - abs(ny - h // 2), -dist_now, dx, dy)
            best = (dx, dy)

    if best is None:
        return [0, 0]
    return [best[0], best[1]]