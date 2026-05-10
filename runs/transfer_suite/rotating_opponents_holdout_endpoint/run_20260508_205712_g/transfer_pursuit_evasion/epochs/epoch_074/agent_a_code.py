def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    sr = str(observation.get("self_role") or "").lower()
    is_evader = not (("pursuer" in sr) or ("pred" in sr) or ("catch" in sr) or ("hunter" in sr))

    obstacles = set()
    for a in observation.get("obstacles") or []:
        if isinstance(a, (list, tuple)) and len(a) >= 2:
            x, y = int(a[0]), int(a[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    moves = [(-1, -1), (-1, 0), (-1, 1),
             (0, -1), (0, 0), (0, 1),
             (1, -1), (1, 0), (1, 1)]

    cx, cy = (w - 1) / 2.0, (h - 1) / 2.0
    best_move = (0, 0)
    best_score = None

    # For evader, also bias toward the corner farthest from pursuer; for pursuer, toward the opponent.
    corners = [(0, 0), (0, h - 1), (w - 1, 0), (w - 1, h - 1)]
    if is_evader:
        tx, ty = max(corners, key=lambda c: abs(c[0] - ox) + abs(c[1] - oy))
    else:
        tx, ty = ox, oy

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue
        d2 = (nx - ox) * (nx - ox) + (ny - oy) * (ny - oy)
        toward_tx = abs(nx - tx) + abs(ny - ty)
        center = (nx - cx) * (nx - cx) + (ny - cy) * (ny - cy)

        if is_evader:
            # Maximize distance from pursuer; keep moving toward farthest corner; slightly prefer center when corner tie.
            score = (d2 * 4.0) - (toward_tx * 0.6) - (center * 0.08)
        else:
            # Minimize distance to pursuer; keep moving toward opponent; slightly prefer center.
            score = (-d2 * 4.0) - (toward_tx * 0.6) - (center * 0.08)

        # Deterministic tie-break: lexicographic preference by (score, -abs(dx)-abs(dy), dx, dy)
        if best_score is None or score > best_score:
            best_score = score
            best_move = (dx, dy)
        elif score == best_score:
            cand = (-(abs(dx) + abs(dy)), dx, dy)
            best_cand = (-(abs(best_move[0]) + abs(best_move[1])), best_move[0], best_move[1])
            if cand > best_cand:
                best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]