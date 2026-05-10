def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    role = (observation.get("self_role") or "").lower()
    is_evader = ("evader" in role) or ("escape" in role) or ("evade" in role) or ("runner" in role)

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def inside(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def free_nbr_count(x, y):
        c = 0
        for dx, dy in moves:
            nx, ny = x + dx, y + dy
            if inside(nx, ny):
                c += 1
        return c

    def dist(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    best = (0, 0)
    best_score = -10**9 if is_evader else 10**9

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inside(nx, ny):
            continue
        d = dist((nx, ny), (ox, oy))
        fn = free_nbr_count(nx, ny)
        # Encourage safer mobility; for evader maximize distance, for pursuer minimize distance.
        # If capture is possible (only when exactly same cell), avoid getting captured when evader.
        score = d if is_evader else -d
        score += (fn * (0.6 if is_evader else 0.3))
        # Center bias to prevent hugging obstacles too early; evader uses it lightly, pursuer slightly.
        cx, cy = (w - 1) / 2.0, (h - 1) / 2.0
        center = -((nx - cx) * (nx - cx) + (ny - cy) * (ny - cy))**0.5
        score += center * (0.05 if is_evader else 0.08)
        # Hard penalty/bonus for immediate capture states.
        if (nx, ny) == (ox, oy):
            score += (-1e6 if is_evader else 1e6)

        if is_evader:
            if score > best_score:
                best_score = score
                best = (dx, dy)
            elif score == best_score:
                # deterministic tie-break: prefer staying if allowed, else lowest lex
                if (dx, dy) == (0, 0) or (dx, dy) < best:
                    best = (dx, dy)
        else:
            if score < best_score:
                best_score = score
                best = (dx, dy)
            elif score == best_score:
                if (dx, dy) == (0, 0) or (dx, dy) < best:
                    best = (dx, dy)

    return [int(best[0]), int(best[1])]