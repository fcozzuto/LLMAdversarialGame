def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    resources = observation.get("resources", []) or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    if not resources:
        # Drift to center while avoiding same row as opponent when possible.
        tx = (w - 1) // 2
        ty = (h - 1) // 2
        best = None
        bestv = None
        for mx, my in moves:
            nx, ny = sx + mx, sy + my
            if not inb(nx, ny) or (nx, ny) in obstacles:
                continue
            row_pen = 0 if ny != oy else 2
            center_d = abs(nx - tx) + abs(ny - ty)
            # Prefer moves that keep within bounds and reduce center distance.
            v = (row_pen, center_d, abs(nx - ox) + abs(ny - oy))
            if bestv is None or v < bestv:
                bestv = v
                best = (mx, my)
        return list(best if best is not None else (0, 0))

    # Evaluate each candidate move by considering the best resource we could aim for next.
    # Primary: maximize lead on that resource (opp_d - self_d). Secondary: favor closer approach.
    # Tactical: penalize landing on opponent's row (sweep_rows-like pressure).
    best_move = (0, 0)
    best_score = None
    for mx, my in moves:
        nx, ny = sx + mx, sy + my
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue

        row_pen = 1 if ny == oy else 0

        # Find best resource to "beat" from next position; no randomness.
        cur_best = None
        for rx, ry in resources:
            sd = abs(nx - rx) + abs(ny - ry)
            od = abs(ox - rx) + abs(oy - ry)
            lead = od - sd  # higher is better
            # Small preference for nearer resource and safer positioning vs opponent.
            # (Tie-breakers are deterministic.)
            v = (lead, -sd, -((abs(nx - ox) + abs(ny - oy)) == 0), -(abs(nx - ox) + abs(ny - oy)))
            if cur_best is None or v > cur_best:
                cur_best = v

        v = (cur_best[0] - row_pen * 0.5, cur_best[1], cur_best[3])
        if best_score is None or v > best_score:
            best_score = v
            best_move = (mx, my)

    return [int(best_move[0]), int(best_move[1])]