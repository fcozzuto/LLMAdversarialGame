def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w, h = observation["grid_width"], observation["grid_height"]
    resources = observation.get("resources") or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles") or []))
    if not resources:
        return [0, 0]

    def md(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx + dy

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best_move = (0, 0)
    best_val = None

    # Prefer moves that (1) improve immediate distance advantage to the best contestable resource,
    # (2) reduce our own distance to the closest remaining resource.
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h):
            continue
        if (nx, ny) in obstacles:
            continue

        # Choose the resource that would be most favorable to contest from this next cell.
        # Tie-break: smaller self distance, then smaller coordinate.
        chosen = None
        chosen_key = None
        for rx, ry in resources:
            sd = md(nx, ny, rx, ry)
            od = md(ox, oy, rx, ry)
            # Higher is better; we convert to minimization by using negative advantage.
            adv = od - sd  # positive means we are closer than opponent
            key = (-adv, sd, rx, ry)
            if chosen_key is None or key < chosen_key:
                chosen_key = key
                chosen = (rx, ry, sd, od)

        rx, ry, sd, od = chosen
        # Extra term: closer to the closest resource overall from next cell.
        closest_sd = None
        for p in resources:
            t = md(nx, ny, p[0], p[1])
            if closest_sd is None or t < closest_sd:
                closest_sd = t

        # Evaluate: primarily maximize adv, then minimize sd, then minimize closest_sd, deterministic tie.
        val = (sd - od, sd, closest_sd, rx, ry, dx, dy)  # all minimized
        if best_val is None or val < best_val:
            best_val = val
            best_move = (dx, dy)

    return [best_move[0], best_move[1]]