def choose_move(observation):
    w = observation.get("grid_width", 8) or 8
    h = observation.get("grid_height", 8) or 8
    w, h = int(w), int(h)

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

    role = str(observation.get("self_role") or "").lower()
    is_evader = "evader" in role

    deltas = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    # Prefer deterministic tie-breaking by fixed candidate ordering above.
    best_score = None
    best_move = [0, 0]

    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        blocked = (nx, ny) in obstacles
        if blocked:
            continue

        mdx, mdy = nx - ox, ny - oy
        dist2 = mdx * mdx + mdy * mdy

        edge = (nx == 0 or nx == w - 1 or ny == 0 or ny == h - 1)
        corner = (nx == 0 or nx == w - 1) and (ny == 0 or ny == h - 1)

        # If pursuer: go to minimize distance; if evader: maximize distance.
        base = (-dist2) if not is_evader else (dist2)

        # Extra shaping: pursuer hugs line towards evader; evader stays on edges/corners.
        # Use opponent Manhattan to add directional pressure without full search.
        manh = abs(nx - ox) + abs(ny - oy)
        shape = 0
        if not is_evader:
            shape = -manh + (1 if edge else 0) * (-0.1)
        else:
            shape = manh * 0.05 + (2.0 if edge else 0.0) + (3.0 if corner else 0.0)

        # Avoid stepping "past" opponent when evading to reduce zigzag collisions.
        # If moving towards opponent (evader) or away (pursuer), penalize slightly.
        prev_manh = abs(sx - ox) + abs(sy - oy)
        new_manh = manh
        if is_evader:
            if new_manh < prev_manh:
                shape -= 0.25
        else:
            if new_manh > prev_manh:
                shape -= 0.25

        score = base + shape
        if best_score is None or score > best_score:
            best_score = score
            best_move = [dx, dy]

    return [int(best_move[0]), int(best_move[1])]