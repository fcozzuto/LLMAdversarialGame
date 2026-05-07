def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    resources = observation.get("resources", []) or []
    obstacles_list = observation.get("obstacles", []) or []
    obstacles = set()
    for p in obstacles_list:
        if isinstance(p, (list, tuple)) and len(p) == 2:
            obstacles.add((p[0], p[1]))

    ox, oy = observation.get("opponent_position", (None, None))
    opp_exists = (ox is not None and oy is not None)

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    # Candidate moves
    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    valid = []
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if inb(nx, ny) and (nx, ny) not in obstacles:
            valid.append((dx, dy, nx, ny))
    if not valid:
        return [0, 0]

    # No visible resources: move to a safe corner-adjacent sweep-block position (deterministic)
    if not resources:
        # Prefer moving to top-right if possible, otherwise bottom-left, to disrupt row sweeps
        prefer = (w - 1, 0) if (sx + sy) % 2 == 0 else (0, h - 1)
        best = (-10**18, 0, 0)
        for dx, dy, nx, ny in valid:
            sc = -((nx - prefer[0]) ** 2 + (ny - prefer[1]) ** 2)
            if sc > best[0]:
                best = (sc, dx, dy)
        return [best[1], best[2]]

    # Score next step by how much we beat the opponent on resource access
    # Also add a small preference to reduce distance to the nearest "best" resource.
    best_overall = (-10**18, 0, 0)
    for dx, dy, nx, ny in valid:
        step_sc = -10**18
        for rx, ry in resources:
            self_d = abs(nx - rx) + abs(ny - ry)
            # approximate time-to-collect: manhattan since diagonal allowed, but still monotonic
            if opp_exists:
                opp_d = abs(ox - rx) + abs(oy - ry)
                access_gap = opp_d - self_d  # larger means we are closer than opponent
            else:
                access_gap = 0

            # slight bonus for reaching sooner (even if gap small)
            tie_break = -self_d * 0.03
            # deterministic shaping to oppose row-sweep: prefer resources whose row is closer to opponent row
            row_shape = -abs(ry - oy) * 0.01 if opp_exists else 0.0

            sc = access_gap * 1.0 + tie_break + row_shape
            if sc > step_sc:
                step_sc = sc
        if step_sc > best_overall[0]:
            best_overall = (step_sc, dx, dy)

    return [best_overall[1], best_overall[2]]