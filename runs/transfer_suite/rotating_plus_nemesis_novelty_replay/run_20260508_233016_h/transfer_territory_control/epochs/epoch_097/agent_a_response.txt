def choose_move(observation):
    sx, sy = observation["self_position"]
    w, h = observation["grid_width"], observation["grid_height"]
    ox, oy = observation["opponent_position"]

    selfT = set(tuple(p) for p in observation.get("self_territory") or [])
    oppT = set(tuple(p) for p in observation.get("opponent_territory") or [])
    unclaimed = observation.get("unclaimed_cells") or []
    obstacles = set(tuple(p) for p in observation.get("obstacles") or [])

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def man(ax, ay, bx, by):
        return abs(ax - bx) + abs(ay - by)

    candidates = [(-1, -1), (-1, 0), (-1, 1),
                  (0, -1), (0, 0), (0, 1),
                  (1, -1), (1, 0), (1, 1)]

    best_target = None
    best_key = None
    if unclaimed:
        # Prefer unclaimed near our side, but with some pressure toward opponent area (center fight).
        # Also favor border cells to avoid getting boxed in.
        for x, y in unclaimed:
            border = (x == 0 or x == w - 1 or y == 0 or y == h - 1)
            # Lower key is better.
            key = (man(x, y, sx, sy) * 2.0 +
                   man(x, y, ox, oy) * 0.6 -
                   (20.0 if border else 0.0))
            if best_key is None or key < best_key:
                best_key = key
                best_target = (x, y)

    best_move = (0, 0)
    best_score = -10**18

    for dx, dy in candidates:
        nx, ny = sx + dx, sy + dy
        if (nx, ny) in obstacles or not inb(nx, ny):
            continue
        score = 0

        # Immediate capture/containment bias.
        if (nx, ny) in oppT:
            score += 2500
        elif (nx, ny) in unclaimed:
            score += 120
        elif (nx, ny) in selfT:
            score += 8
        else:
            score -= 5

        # Frontier direction bias toward best target (if any).
        if best_target is not None:
            tx, ty = best_target
            d_now = man(sx, sy, tx, ty)
            d_next = man(nx, ny, tx, ty)
            score += (d_now - d_next) * 35.0

            # If too close to opponent, gently steer away.
            score += (man(nx, ny, ox, oy) - man(sx, sy, ox, oy)) * 2.5

            # Avoid stepping into the opponent's "zone" unless capturing.
            if (nx, ny) not in oppT:
                if man(nx, ny, ox, oy) <= 2:
                    score -= 60

        # Prefer moves that increase distance from obstacles are unnecessary; keep deterministic tie-break.
        if score > best_score or (score == best_score and (dx, dy) < best_move):
            best_score = score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]