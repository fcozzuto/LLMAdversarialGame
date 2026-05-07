def choose_move(observation):
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    res = observation.get("resources") or []
    obs_list = observation.get("obstacles") or []
    obstacles = obs_list if isinstance(obs_list, set) else set(tuple(p) for p in obs_list)

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    valid_resources = []
    for r in res:
        rx, ry = r
        if (rx, ry) not in obstacles:
            valid_resources.append((rx, ry))
    if not valid_resources:
        return [0, 0]

    candidates = []
    for dx, dy in [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]:
        nx, ny = sx + dx, sy + dy
        if nx < 0 or nx >= w or ny < 0 or ny >= h:
            continue
        if (nx, ny) in obstacles:
            continue
        candidates.append((dx, dy, nx, ny))
    if not candidates:
        return [0, 0]

    # Pick a small deterministic set of "most contested" resources to evaluate.
    scored = []
    for rx, ry in valid_resources:
        dS = cheb(sx, sy, rx, ry)
        dO = cheb(ox, oy, rx, ry)
        advantage = dO - dS  # positive means we are closer
        scored.append((advantage, -dS, rx, ry))
    scored.sort(reverse=True)
    top = scored[:3] if len(scored) >= 3 else scored

    best = None
    best_key = None
    for dx, dy, nx, ny in candidates:
        # Evaluate moves by how they swing reachability on contested resources,
        # plus a tie-break favoring smaller own distance to the best target.
        key = 0
        min_dS_after = None
        for adv, ndS, rx, ry in top:
            dS_a = cheb(nx, ny, rx, ry)
            dO = cheb(ox, oy, rx, ry)
            swing = dO - dS_a
            # Encourage positive swing heavily; still account for denial when negative.
            key += (swing * 10 + (1 if dS_a == 0 else 0))
            if min_dS_after is None or dS_a < min_dS_after:
                min_dS_after = dS_a
        tie = (-min_dS_after if min_dS_after is not None else 0)
        move_key = (key, tie, dx, dy)
        if best_key is None or move_key > best_key:
            best_key = move_key
            best = (dx, dy)
    return [best[0], best[1]]