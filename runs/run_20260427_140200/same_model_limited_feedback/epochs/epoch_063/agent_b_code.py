def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", []) or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))
    if not resources:
        return [0, 0]

    def dist(a, b, c, d):
        dx = a - c
        dy = b - d
        if dx < 0: dx = -dx
        if dy < 0: dy = -dy
        return dx if dx > dy else dy  # king-move distance

    def clamp(x, lo, hi):
        return lo if x < lo else (hi if x > hi else x)

    # Pick a target resource where we have (or can build) the best time advantage.
    best_res = None
    best_adv = None
    for rx, ry in resources:
        ds = dist(sx, sy, rx, ry)
        do = dist(ox, oy, rx, ry)
        adv = do - ds
        # Prefer higher advantage; tie-break by closer to us, then by lexicographic position.
        if best_res is None or adv > best_adv or (adv == best_adv and (ds < dist(sx, sy, best_res[0], best_res[1]) or
            (ds == dist(sx, sy, best_res[0], best_res[1]) and (rx, ry) < best_res))):
            best_res = (rx, ry)
            best_adv = adv

    rx, ry = best_res

    # Candidate moves
    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    best_move = (0, 0)
    best_score = None

    # For subtle strategic change: also consider stealing the opponent's likely target by biasing away
    # from cells that increase our disadvantage for the current best target.
    curr_ds = dist(sx, sy, rx, ry)
    for dx, dy in moves:
        nx = clamp(sx + dx, 0, w - 1)
        ny = clamp(sy + dy, 0, h - 1)
        if (nx, ny) in obstacles:
            continue
        nds = dist(nx, ny, rx, ry)
        nod = dist(ox, oy, rx, ry)
        advantage = nod - nds

        # Also keep pressure: prefer reducing distance to the nearest resource from the candidate cell.
        nearest = None
        for tx, ty in resources:
            d = dist(nx, ny, tx, ty)
            if nearest is None or d < nearest or (d == nearest and (tx, ty) < (nearestx, nearesty)):
                nearest = d
                nearestx, nearesty = tx, ty

        # Score: minimize distance to target, maximize advantage, and avoid regression.
        score = (advantage * 10) - nds
        if nds > curr_ds:
            score -= 3
        score += (20 - nearest) * 0.2  # small tie-break toward general resource proximity

        if best_score is None or score > best_score or (score == best_score and (nx, ny) < (sx + best_move[0], sy + best_move[1])):
            best_score = score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]