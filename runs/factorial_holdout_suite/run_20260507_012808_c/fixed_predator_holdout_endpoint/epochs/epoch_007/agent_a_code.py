def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", []) or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    moves = []
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            if inb(nx, ny) and (nx, ny) not in obstacles:
                moves.append((dx, dy))

    if not moves:
        return [0, 0]
    if not resources:
        # Go to center-ish deterministically
        cx, cy = w // 2, h // 2
        best = None
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            d = abs(nx - cx) + abs(ny - cy)
            cand = (d, dx, dy)
            if best is None or cand < best:
                best = cand
        return [best[1], best[2]]

    def man(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    # Score a position by best guaranteed resource advantage, else denial.
    # Prefer: larger (opp_dist - self_dist). Tie-break: smaller self_dist.
    def pos_score(px, py):
        best = None
        for rx, ry in resources:
            sd = man(px, py, rx, ry)
            od = man(ox, oy, rx, ry)
            adv = od - sd
            # Encourage closer resources too
            cand = (-adv, sd, rx, ry)
            if best is None or cand < best:
                best = cand
        # return original ordering for comparison outside: higher adv better, lower sd better
        # Using best tuple to keep deterministic ordering:
        return best

    best_move = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        sc = pos_score(nx, ny)
        # Convert back to comparable tuple where smaller is better:
        # We already used a "smaller-is-better" tuple in pos_score.
        cand = (sc, dx, dy)
        if best_move is None or cand < best_move:
            best_move = cand

    return [best_move[1], best_move[2]]