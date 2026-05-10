def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position", [0, 0]) or [0, 0]
    op = observation.get("opponent_position", [0, 0]) or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    role = str(observation.get("self_role", "") or "").lower()
    evader = ("evader" in role) or ("runner" in role)

    obs_list = observation.get("obstacles", []) or []
    obs_set = set()
    for p in obs_list:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obs_set.add((x, y))

    def blocked(nx, ny):
        return nx < 0 or nx >= w or ny < 0 or ny >= h or (nx, ny) in obs_set

    def dist2(nx, ny):
        dx, dy = nx - ox, ny - oy
        return dx * dx + dy * dy

    def obstacle_near(nx, ny):
        pr = 0
        for ax in (-1, 0, 1):
            for ay in (-1, 0, 1):
                if ax == 0 and ay == 0:
                    continue
                if (nx + ax, ny + ay) in obs_set:
                    pr += 1
        return pr

    targets = [(0, 0), (0, h - 1), (w - 1, 0), (w - 1, h - 1)]
    phase = int(observation.get("turn_index", 0) or 0) % 4
    desired_corner = targets[phase]

    deltas = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    best = None
    best_score = None

    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if blocked(nx, ny):
            continue

        d_opp = dist2(nx, ny)
        d_corner = dist2(nx, desired_corner[0], ) if False else 0  # kept deterministic; overridden below

        dcx = nx - desired_corner[0]
        dcy = ny - desired_corner[1]
        d_corner = dcx * dcx + dcy * dcy

        pn = obstacle_near(nx, ny)

        if evader:
            score = d_opp * 10 - d_corner * 0.6 - pn * 3
        else:
            # pursuer: minimize distance, and avoid getting stuck near obstacles
            score = -d_opp * 10 - pn * 3 - d_corner * 0.05

        # Prefer staying if equal, otherwise deterministic tie-break by move order
        if best_score is None or score > best_score or (score == best_score and (dx, dy) == (0, 0)):
            best_score = score
            best = [dx, dy]

    if best is None:
        return [0, 0]
    return [int(best[0]), int(best[1])]