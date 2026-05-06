def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [w - 1, h - 1])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for r in observation.get("resources") or []:
        if r and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))
    if not resources:
        return [0, 0]

    def man(ax, ay, bx, by):
        return abs(ax - bx) + abs(ay - by)

    moves = [(-1, -1), (0, -1), (1, -1),
             (-1, 0), (0, 0), (1, 0),
             (-1, 1), (0, 1), (1, 1)]

    # Pick a target resource emphasizing denial: maximize (opp_dist - my_dist).
    # If all are bad, still pick deterministically by best (closest to us).
    best_res = None
    best_res_key = None
    for rx, ry in resources:
        d_us = man(sx, sy, rx, ry)
        d_opp = man(ox, oy, rx, ry)
        denial = d_opp - d_us
        # Prefer resources not immediately adjacent to opponent (reduce immediate lock-in).
        adj_pen = 0
        if man(ox, oy, rx, ry) <= 2:
            adj_pen = 2
        key = (-(denial - adj_pen), d_us, rx, ry)
        if best_res_key is None or key < best_res_key:
            best_res_key = key
            best_res = (rx, ry)

    tx, ty = best_res

    # Choose the move that best improves our situation vs target and opponent.
    best_move = None
    best_key = None
    cur_opp_dist = man(sx, sy, ox, oy)

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h):
            continue
        if (nx, ny) in obstacles:
            continue

        d_us = man(nx, ny, tx, ty)
        d_opp = man(ox, oy, tx, ty)
        denial_score = d_opp - d_us  # larger is better

        # Keep some separation from opponent to avoid being herded/denied.
        new_opp_dist = man(nx, ny, ox, oy)
        sep_gain = new_opp_dist - cur_opp_dist

        # Small bias to reduce distance to target, then deterministic tie-break.
        dist_to_target = d_us

        key = (-(denial_score + 0.5 * sep_gain), dist_to_target, dx, dy)
        if best_key is None or key < best_key:
            best_key = key
            best_move = (dx, dy)

    if best_move is None:
        return [0, 0]
    return [int(best_move[0]), int(best_move[1])]