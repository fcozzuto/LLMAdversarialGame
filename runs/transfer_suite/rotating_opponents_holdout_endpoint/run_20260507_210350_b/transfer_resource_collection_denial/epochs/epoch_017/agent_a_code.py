def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    obstacles = set(tuple(p) for p in observation.get("obstacles", []))
    resources = [tuple(p) for p in observation.get("resources", []) if tuple(p) not in obstacles]
    if not resources:
        return [0, 0]

    def man(a, b, c, d):
        return abs(a - c) + abs(b - d)

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    def valid(nx, ny):
        return 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles

    # Pick target: prefer resources where we can realistically contest; otherwise go for best alternative.
    best = None  # tuple compare
    for tx, ty in resources:
        sd = man(sx, sy, tx, ty)
        od = man(ox, oy, tx, ty)
        # contest_margin <0 means opponent closer
        contest_margin = od - sd
        # deterministically break ties by cell hash-like value
        tie = (tx * 97 + ty * 31 + sd * 7 + od * 13) % 997
        # Strategy:
        # - If we are not behind, strongly prefer these; then shorter our distance.
        # - If behind, only pick if it's much better than other options (we may still reach first via diagonal/turns).
        if sd <= od:
            cand = (0, contest_margin, sd, tie, tx, ty)
        else:
            # behind: require meaningful advantage to consider; otherwise leave space for contest later
            cand = (1, abs(contest_margin), sd, tie, tx, ty)
        if best is None or cand < best:
            best = cand
    _, _, _, _, tx, ty = best

    # Choose move: minimize distance to target; among equals, maximize distance from opponent; avoid obstacles/outside.
    best_move = None  # (dist_to_target, -dist_to_opp, tie, dx, dy)
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        dt = man(nx, ny, tx, ty)
        do = man(nx, ny, ox, oy)
        tie = ((nx * 53 + ny * 19 + dt * 3 + do * 5) % 103)
        cand = (dt, -do, tie, dx, dy)
        if best_move is None or cand < best_move:
            best_move = cand

    if best_move is None:
        return [0, 0]
    return [best_move[3], best_move[4]]