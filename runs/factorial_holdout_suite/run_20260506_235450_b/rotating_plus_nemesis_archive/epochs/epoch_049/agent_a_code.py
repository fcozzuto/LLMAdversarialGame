def choose_move(observation):
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    resources = observation.get("resources") or []
    obstacles = observation.get("obstacles") or []

    obs = set()
    for p in obstacles:
        if p and len(p) >= 2:
            obs.add((int(p[0]), int(p[1])))

    def man(ax, ay, bx, by):
        return abs(ax - bx) + abs(ay - by)

    def is_free(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obs

    if not resources:
        return [0, 0]

    best = None
    best_key = None
    for rx, ry in resources:
        sd = man(sx, sy, rx, ry)
        od = man(ox, oy, rx, ry)
        # Prefer resources we can reach at least as fast; otherwise still try to reduce opponent lead.
        lead = od - sd  # positive means we are ahead
        key = (0 if lead >= 0 else 1, -lead, sd, rx * 31 + ry)
        if best_key is None or key < best_key:
            best_key = key
            best = (rx, ry)

    tx, ty = best
    dx = 0 if tx == sx else (1 if tx > sx else -1)
    dy = 0 if ty == sy else (1 if ty > sy else -1)

    candidates = []
    # Try direct diagonal/orthogonal first, then fallback options in deterministic order.
    candidates.append((dx, dy))
    candidates.append((dx, 0))
    candidates.append((0, dy))
    candidates.append((dx, -dy))
    candidates.append((-dx, dy))
    candidates.append((-dx, 0))
    candidates.append((0, -dy))
    candidates.append((0, 0))

    cur_dist = man(sx, sy, tx, ty)
    best_step = (0, 0)
    best_improve = -10**9
    for stepx, stepy in candidates:
        nx, ny = sx + stepx, sy + stepy
        if not is_free(nx, ny):
            continue
        nd = man(nx, ny, tx, ty)
        # Secondary tie-break: keep moving in direction that also reduces opponent's distance to same target.
        opp_d = man(ox, oy, tx, ty)
        improve = (cur_dist - nd) * 100 + (opp_d - opp_d)  # keep deterministic; opponent term constant
        if improve > best_improve:
            best_improve = improve
            best_step = (stepx, stepy)

    return [int(best_step[0]), int(best_step[1])]