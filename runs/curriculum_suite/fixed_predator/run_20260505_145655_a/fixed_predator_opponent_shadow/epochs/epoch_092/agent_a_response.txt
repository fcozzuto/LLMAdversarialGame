def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    x, y = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", []) or []
    obs_list = observation.get("obstacles", []) or []
    obstacles = set((p[0], p[1]) for p in obs_list)

    def sign(v):
        return 0 if v == 0 else (1 if v > 0 else -1)

    def in_bounds(nx, ny):
        return 0 <= nx < w and 0 <= ny < h

    def man(a, b, c, d):
        return abs(a - c) + abs(b - d)

    def cell_value(nx, ny):
        if not resources:
            # chase/deny: move toward opponent while keeping some progress
            return -man(nx, ny, ox, oy)
        best = None
        bestv = None
        for tx, ty in resources:
            self_d = man(nx, ny, tx, ty)
            opp_d = man(ox, oy, tx, ty)
            v = (opp_d - self_d) * 1000 - self_d
            if bestv is None or v > bestv or (v == bestv and (opp_d < bestv_oppd)):
                bestv = v
                bestv_oppd = opp_d
                best = (tx, ty)
        return bestv if bestv is not None else -10**9

    if not resources:
        return [-sign(ox - x), -sign(oy - y)]

    # Choose best move among 9 options with deterministic tie-break.
    moves = []
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = x + dx, y + dy
            if not in_bounds(nx, ny):
                continue
            if (nx, ny) in obstacles:
                continue
            # Prioritize moving toward a high-value resource, but also deny opponent advantage.
            v = cell_value(nx, ny)
            dist_self_to_opp = man(nx, ny, ox, oy)
            # tie-break: prefer diagonal advancement, then closer to opponent
            diag_bonus = 1 if dx != 0 and dy != 0 else 0
            key = (v, diag_bonus, -dist_self_to_opp, -(abs(dx) + abs(dy)), -dx, -dy)
            moves.append((key, [dx, dy]))
    if not moves:
        # If boxed in by obstacles, allow staying.
        return [0, 0]

    moves.sort(key=lambda t: t[0], reverse=True)
    return moves[0][1]