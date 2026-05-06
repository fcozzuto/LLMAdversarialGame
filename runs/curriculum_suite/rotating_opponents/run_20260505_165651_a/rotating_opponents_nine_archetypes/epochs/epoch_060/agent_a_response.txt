def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    resources = observation.get("resources") or []
    obs_list = observation.get("obstacles") or []
    obstacles = set((p[0], p[1]) for p in obs_list)

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def blocked(x, y):
        return (not inb(x, y)) or ((x, y) in obstacles)

    def man(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0:
            dx = -dx
        dy = ay - by
        if dy < 0:
            dy = -dy
        return dx + dy

    # If no resources, stay safe and drift to a corner-to-center diagonal away from opponent.
    if not resources:
        tx = (w - 1) // 2
        ty = (h - 1) // 2
        best_key = None
        best_move = [0, 0]
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if blocked(nx, ny):
                continue
            key = (man(nx, ny, tx, ty), -man(nx, ny, ox, oy))
            if best_key is None or key < best_key:
                best_key = key
                best_move = [dx, dy]
        return best_move

    # Score each resource for a candidate move; prefer getting a resource earlier and denying opponent.
    opp_escape_bias = 0.08
    best_overall = None
    best_move = [0, 0]

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if blocked(nx, ny):
            continue

        opp_d = man(nx, ny, ox, oy)
        # Keep some distance when we're not making a clearly winning approach to a resource.
        safety = -opp_escape_bias * opp_d

        best_res_score = None
        for rx, ry in resources:
            md = man(nx, ny, rx, ry)
            od = man(ox, oy, rx, ry)
            # Lower is better:
            # - Prefer smaller own distance (md)
            # - Prefer when we are closer than opponent (md-od)
            # - Strongly discourage stepping into a resource where opponent is much closer
            contest = md - od
            penalty_if_behind = 4 * (1 if od + 1 < md else 0)
            score = md + 0.9 * contest + penalty_if_behind
            if best_res_score is None or score < best_res_score:
                best_res_score = score

        # If opponent is extremely close, prioritize safety slightly.
        close_opp = 1 if man(nx, ny, ox, oy) <= 2 else 0
        key = (best_res_score + safety + 2.0 * close_opp, -man(nx, ny, ox, oy))
        if best_overall is None or key < best_overall:
            best_overall = key
            best_move = [dx, dy]

    return best_move