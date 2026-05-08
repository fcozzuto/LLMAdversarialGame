def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    obstacles = set(tuple(p) for p in observation["obstacles"] or [])
    resources = observation["resources"] or []

    if not resources:
        return [0, 0]

    # Pick best resource: prioritize those we can get earlier than opponent; otherwise nearest-but-closest-to-win.
    best_r = None
    best_key = None
    for rx, ry in resources:
        dself = (rx - sx) * (rx - sx) + (ry - sy) * (ry - sy)
        dopp = (rx - ox) * (rx - ox) + (ry - oy) * (ry - oy)
        # key: maximize (dopp - dself), then minimize dself (break ties deterministically)
        key = (-(dopp - dself), dself, rx, ry)
        if best_key is None or key < best_key:
            best_key = key
            best_r = (rx, ry)

    rx, ry = best_r

    # If opponent is significantly closer to the best resource, head to a different resource that we can beat or reduce contest.
    # (simple second pass)
    dself0 = (rx - sx) * (rx - sx) + (ry - sy) * (ry - sy)
    dopp0 = (rx - ox) * (rx - ox) + (ry - oy) * (ry - oy)
    if dopp0 + 1 < dself0 and len(resources) > 1:
        alt = None
        alt_key = None
        for ax, ay in resources:
            dself = (ax - sx) * (ax - sx) + (ay - sy) * (ay - sy)
            dopp = (ax - ox) * (ax - ox) + (ay - oy) * (ay - oy)
            # require we are not worse by too much; then maximize gap
            if dself > dopp + 4:
                continue
            key = (-(dopp - dself), dself, ax, ay)
            if alt_key is None or key < alt_key:
                alt_key = key
                alt = (ax, ay)
        if alt is not None:
            rx, ry = alt

    # Candidate moves: 8-neighborhood + stay, deterministic ordering, avoid obstacles.
    candidates = []
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles:
                candidates.append((dx, dy))

    if not candidates:
        return [0, 0]

    # Scoring move: minimize distance to target; add penalty for being too close to opponent unless it helps reach target.
    best_move = None
    best_score = None
    for dx, dy in candidates:
        nx, ny = sx + dx, sy + dy
        dist_to_target = (rx - nx) * (rx - nx) + (ry - ny) * (ry - ny)
        dist_to_opp = (ox - nx) * (ox - nx) + (oy - ny) * (oy - ny)

        # Aggression/contesting: prefer moves that also increase opponent distance if we can get to target soon.
        # If opponent is near, discourage stepping into adjacency (shadow archetype likely pressure).
        opp_pen = 0
        if dist_to_opp <= 2:
            opp_pen += 20
        if dist_to_target <= 5:
            opp_pen -= 3  # small preference to keep pressure when we're close to collecting routes

        # Also discourage moves that step "past" the target (increase Manhattan alignment mismatch deterministically).
        # Using dot product toward target.
        tx, ty = rx - sx, ry - sy
        step_dot = dx * (rx - nx) + dy * (ry - ny)  # lower is "worse"; we want closer
        score = (dist_to_target + opp_pen, dist_to_opp, step_dot, dx, dy)
        if best_score is None or score < best_score:
            best_score = score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]