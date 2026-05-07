def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    resources = observation.get("resources", []) or []
    if not resources:
        return [0, 0]
    obstacles = set((p[0], p[1]) for p in (observation.get("obstacles", []) or []))
    turn = int(observation.get("turn_index", 0) or 0)

    def md(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    # Pick a target: prefer resources we can reach sooner than opponent, else best "denial" target near opponent.
    best = None
    for rx, ry in resources:
        sd = md(sx, sy, rx, ry)
        od = md(ox, oy, rx, ry)
        lead = od - sd  # positive means we are closer
        # Two-level preference: win/secure if we can beat them; otherwise still move toward high lead/denial.
        val = (lead, -sd, -od, rx, ry) if lead >= 0 else (-sd, lead, -od, rx, ry)
        if best is None or val > best[0]:
            best = (val, rx, ry)
    _, tx, ty = best

    moves = [(-1, 0), (1, 0), (0, -1), (0, 1), (-1, -1), (-1, 1), (1, -1), (1, 1), (0, 0)]
    start = turn % len(moves)
    moves = moves[start:] + moves[:start]

    def valid(nx, ny):
        return 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles

    # Prefer moves that reduce our distance to target; break ties by reducing opponent distance more.
    cur_s = md(sx, sy, tx, ty)
    cur_o = md(ox, oy, tx, ty)
    best_move = [0, 0]
    best_tuple = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        ns = md(nx, ny, tx, ty)
        no = md(ox, oy, tx, ty)  # opponent position unchanged this turn
        step_gain = cur_s - ns
        # Also allow slight increase if it blocks opponent's likely path (proxy: maximize our lead improvement).
        opp_lead = md(ox, oy, tx, ty) - ns
        tup = (step_gain, opp_lead, -ns, abs(nx - ox) + abs(ny - oy), -dx * dx - dy * dy, nx, ny)
        if best_tuple is None or tup > best_tuple:
            best_tuple = tup
            best_move = [dx, dy]

    if best_tuple is None:
        # All moves blocked: stay (engine will keep position if invalid).
        return [0, 0]
    return best_move