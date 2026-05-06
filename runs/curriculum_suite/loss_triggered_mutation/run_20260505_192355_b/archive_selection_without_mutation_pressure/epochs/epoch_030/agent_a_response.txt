def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    resources = observation.get("resources") or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles") or []))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    if not resources:
        return [0, 0]

    def manh(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best = None

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue

        # Evaluate move by best contestable resource from the new position
        best_move_score = None
        for rx, ry in resources:
            myd = manh(nx, ny, rx, ry)
            opd = manh(ox, oy, rx, ry)
            adv = opd - myd  # >=0 means we arrive no later than opponent
            # Prefer winning/contesting (adv>=0), then most advantage, then closer resources
            winflag = 1 if adv >= 0 else 0
            closer = -myd
            score = (winflag, adv, closer, -abs(rx - ox) - abs(ry - oy))
            if best_move_score is None or score > best_move_score:
                best_move_score = score

        # Global tie-break: determinism via dx,dy ordering embedded in comparisons
        if best is None or best_move_score > best[0] or (best_move_score == best[0] and (dx, dy) < best[1]):
            best = (best_move_score, (dx, dy))

    if best is None:
        return [0, 0]
    return [best[1][0], best[1][1]]