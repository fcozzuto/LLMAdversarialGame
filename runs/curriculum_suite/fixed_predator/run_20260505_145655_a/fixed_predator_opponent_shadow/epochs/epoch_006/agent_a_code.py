def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    x, y = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", [])
    obstacles = set(tuple(p) for p in observation.get("obstacles", []))

    def in_bounds(nx, ny):
        return 0 <= nx < w and 0 <= ny < h

    def man(a, b, c, d):
        dx = a - c
        dy = b - d
        if dx < 0:
            dx = -dx
        if dy < 0:
            dy = -dy
        return dx + dy

    dirs = [(0, 0), (1, 0), (-1, 0), (0, 1), (0, -1), (1, 1), (1, -1), (-1, 1), (-1, -1)]
    if not resources:
        dx = 0 if ox == x else (1 if ox > x else -1)
        dy = 0 if oy == y else (1 if oy > y else -1)
        return [-dx, -dy]

    # Choose targets that we can reach at least as fast as (or faster than) the opponent; otherwise prefer a "best contest" one.
    def target_score(px, py):
        best = None
        best_key = None
        for rx, ry in resources:
            my_md = man(px, py, rx, ry)
            opp_md = man(ox, oy, rx, ry)
            # If we can contest or win, strongly prefer; else penalize.
            contest_gap = opp_md - my_md  # positive => we are faster
            key = (
                -(contest_gap if contest_gap > 0 else -contest_gap) if contest_gap <= 0 else -contest_gap,
                my_md,
                rx,
                ry,
            )
            # Separate explicit selection: maximize contest_gap, then minimize my_md, then deterministic coords.
            sel_key = (-contest_gap, my_md, rx, ry)
            if best is None or sel_key < best_key:
                best = (rx, ry)
                best_key = sel_key
        return best

    t = target_score(x, y)

    best_move = (0, 0)
    best_val = -10**18

    for dx, dy in dirs:
        nx, ny = x + dx, y + dy
        if not in_bounds(nx, ny) or (nx, ny) in obstacles:
            continue

        opp_d = man(nx, ny, ox, oy)
        # Update target decision from the candidate position.
        tx, ty = target_score(nx, ny)
        my_to_t = man(nx, ny, tx, ty)

        # Encourage: approach viable target, keep distance from opponent, and reduce opponent's ability to grab our target.
        opp_to_t = man(ox, oy, tx, ty)
        we_are_faster = opp_to_t - my_to_t  # positive => we likely grab first
        value = 0
        value += -my_to_t * 10
        value += we_are_faster * 6
        value += opp_d * 0.8

        # Small preference for moving onto a resource directly
        if (nx, ny) == (tx, ty):
            value += 25

        # Deterministic tie-break: prefer staying, then orthogonal, then diagonals in dirs order already.
        if value > best_val:
            best_val = value
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]