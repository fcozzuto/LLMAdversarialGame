def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [w - 1, h - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    def ok(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    sr = (observation.get("self_role") or "").lower()
    self_is_pursuer = (("purs" in sr) and ("evad" not in sr)) or ("purs" not in sr and "evad" not in sr)
    deltas = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def man(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0:
            dx = -dx
        dy = y1 - y2
        if dy < 0:
            dy = -dy
        return dx + dy

    best = None
    best_score = None
    # Deterministic tie-break via lexicographic preference order in deltas list
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not ok(nx, ny):
            continue
        d = man(nx, ny, ox, oy)
        # If pursuer: minimize distance; if evader: maximize distance.
        score = d if not self_is_pursuer else -d

        # Small obstacle-aware term: penalize moving adjacent to obstacles for pursuer less, for evader more
        adj = 0
        for ax in (-1, 0, 1):
            for ay in (-1, 0, 1):
                if ax == 0 and ay == 0:
                    continue
                if (nx + ax, ny + ay) in obstacles:
                    adj += 1
        score += (-1 if self_is_pursuer else -2) * adj

        if best is None or score > best_score:
            best = [dx, dy]
            best_score = score

    if best is not None:
        return [int(best[0]), int(best[1])]
    return [0, 0]