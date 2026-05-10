def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sx, sy = observation.get("self_position") or (0, 0)
    ox, oy = observation.get("opponent_position") or (w - 1, h - 1)

    obstacles = set((int(x), int(y)) for x, y in (observation.get("obstacles") or []) if x is not None)
    self_t = set((int(x), int(y)) for x, y in (observation.get("self_territory") or []))
    opp_t = set((int(x), int(y)) for x, y in (observation.get("opponent_territory") or []))
    unclaimed = set((int(x), int(y)) for x, y in (observation.get("unclaimed_cells") or []))

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def man(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    # Target selection
    if unclaimed:
        candidates = list(unclaimed)
    elif opp_t:
        # Push toward opponent by aiming at a deterministic "border" proxy:
        # nearest opponent territory cell to our position.
        candidates = list(opp_t)
    else:
        candidates = [(w // 2, h // 2)]

    tx, ty = min(candidates, key=lambda c: (man(sx, sy, c[0], c[1]), c[0], c[1]))

    # Score candidate moves: prefer reducing distance to target; prefer moving into unclaimed/opp,
    # avoid obstacles, and prefer cells we don't already own when target is elsewhere.
    best_move = (0, 0)
    best_score = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        if (nx, ny) in obstacles:
            # Engine will keep us in place; treat as very bad unless no other move exists.
            score = -10_000 + (1 if (dx, dy) == (0, 0) else 0)
        else:
            dist = man(nx, ny, tx, ty)
            # "Territory value" heuristic
            if (nx, ny) in unclaimed:
                val = 3
            elif (nx, ny) in opp_t:
                val = 4
            elif (nx, ny) in self_t:
                val = 1
            else:
                val = 2
            # Pressure toward opponent
            opp_dist = man(nx, ny, ox, oy)
            pressure = -0.05 * opp_dist  # lower is better
            # Slight tie-break bias to keep moving generally toward opponent side
            bias = 0
            if ox != sx:
                bias += -0.01 * (abs(nx - ox))
            score = (-dist) + val + pressure + bias

            # If we are already at the target, don't oscillate too much
            if (sx, sy) == (tx, ty):
                score -= 0.1 * (1 if (dx, dy) != (0, 0) else 0)

        if best_score is None or score > best_score or (score == best_score and (dx, dy) < best_move):
            best_score = score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]