def choose_move(observation):
    x0, y0 = observation["self_position"]
    ox0, oy0 = observation["opponent_position"]
    w, h = observation["grid_width"], observation["grid_height"]
    obstacles = set((p[0], p[1]) for p in observation.get("obstacles", []))
    resources = observation.get("resources", []) or []
    if not resources:
        dx, dy = (0, 0)
        return [dx, dy]

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def dist(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    # Choose a contested target: good for us, worse for opponent
    best_target = None
    best_key = None
    for r in resources:
        ds = dist((x0, y0), r)
        do = dist((ox0, oy0), r)
        key = (do - ds, -ds)  # maximize do-ds, then minimize ds
        if best_key is None or key > best_key:
            best_key = key
            best_target = r

    tx, ty = best_target
    # If opponent is much closer to the chosen target, switch to the resource where we're relatively closest
    do_best = dist((ox0, oy0), (tx, ty))
    ds_best = dist((x0, y0), (tx, ty))
    if do_best < ds_best:
        best_target = None
        best_key = None
        for r in resources:
            ds = dist((x0, y0), r)
            do = dist((ox0, oy0), r)
            key = (ds - do, -ds)  # maximize ds-do, then minimize ds
            if best_key is None or key > best_key:
                best_key = key
                best_target = r
        tx, ty = best_target

    # Evaluate candidate moves by their resulting advantage on targets
    best_move = [0, 0]
    best_score = None
    for dx, dy in moves:
        nx, ny = x0 + dx, y0 + dy
        if nx < 0 or nx >= w or ny < 0 or ny >= h:
            continue
        if (nx, ny) in obstacles:
            continue

        # Score based on best contested resource from next position
        ns_best = None
        no_best = None
        for r in resources:
            ds = dist((nx, ny), r)
            do = dist((ox0, oy0), r)
            # Advantage term, with slight push toward smaller ds
            s = (do - ds) * 10 - ds
            if ns_best is None or s > ns_best:
                ns_best = s
                no_best = r

        # Also keep pressure toward the current target deterministically
        adv_to_target = (dist((ox0, oy0), (tx, ty)) - dist((nx, ny), (tx, ty))) * 2 - dist((nx, ny), (tx, ty)) * 0.1
        score = (ns_best if ns_best is not None else -10**9) + adv_to_target

        if best_score is None or score > best_score:
            best_score = score
            best_move = [dx, dy]
        elif score == best_score:
            # Deterministic tie-breaker: prefer moves that reduce distance to target, then lexicographic
            cur_d = dist((nx, ny), (tx, ty))
            best_d = dist((x0 + best_move[0], y0 + best_move[1]), (tx, ty))
            if cur_d < best_d or (cur_d == best_d and (dx, dy) < (best_move[0], best_move[1])):
                best_move = [dx, dy]

    return [int(best_move[0]), int(best_move[1])]