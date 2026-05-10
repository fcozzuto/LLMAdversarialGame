def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))
    unclaimed = [tuple(p) for p in (observation.get("unclaimed_cells", []) or [])]
    opp_terr = set(tuple(p) for p in (observation.get("opponent_territory", []) or []))
    if not unclaimed:
        tx, ty = (w - 1) / 2.0, (h - 1) / 2.0
    else:
        def inb(x, y):
            return 0 <= x < w and 0 <= y < h

        dirs8 = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

        def adj_to_opp(x, y):
            for dx, dy in dirs8:
                if dx == 0 and dy == 0:
                    continue
                if (x + dx, y + dy) in opp_terr:
                    return True
            return False

        # Deterministic target choice: prioritize unclaimed adjacent to opponent territory.
        # Then prioritize closeness to opponent; lastly closeness to self.
        best = None
        best_key = None
        for x, y in unclaimed:
            if not inb(x, y) or (x, y) in obstacles:
                continue
            near_opp = abs(x - ox) + abs(y - oy)
            k = (
                0 if adj_to_opp(x, y) else 1,
                near_opp,
                abs(x - sx) + abs(y - sy),
                x,
                y,
            )
            if best_key is None or k < best_key:
                best_key = k
                best = (x, y)
        if best is None:
            tx, ty = (w - 1) / 2.0, (h - 1) / 2.0
        else:
            tx, ty = best

    # Greedy step toward target with obstacle avoidance; deterministic tie-break.
    dirs8 = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    def dist2(x, y):
        dx = x - tx
        dy = y - ty
        return dx * dx + dy * dy

    best_step = (0, 0)
    best_score = None
    for dx, dy in dirs8:
        nx, ny = sx + dx, sy + dy
        if (nx, ny) in obstacles or not (0 <= nx < w and 0 <= ny < h):
            continue
        # Slightly prefer progressing, avoid wandering: add a small bias away from current self-target vector.
        score = dist2(nx, ny)
        if best_score is None or score < best_score:
            best_score = score
            best_step = (dx, dy)
        elif best_score is not None and score == best_score:
            if (dx, dy) < best_step:
                best_step = (dx, dy)

    return [int(best_step[0]), int(best_step[1])]