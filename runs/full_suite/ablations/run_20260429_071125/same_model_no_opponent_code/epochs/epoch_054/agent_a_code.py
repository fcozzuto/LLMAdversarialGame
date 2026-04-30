def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obs_cells = set()
    for p in (observation.get("obstacles") or []):
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obs_cells.add((x, y))

    resources = []
    for p in (observation.get("resources") or []):
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obs_cells:
                resources.append((x, y))
    if not resources:
        return [0, 0]

    dirs = [(dx, dy) for dx in (-1, 0, 1) for dy in (-1, 0, 1)]
    dirs.sort()

    def cheb(a, b):
        dx = a[0] - b[0]
        if dx < 0:
            dx = -dx
        dy = a[1] - b[1]
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    def inside(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obs_cells

    # Prefer resources we can reach sooner than opponent; if none, prefer still-valuable close to us.
    ranked = []
    for tx, ty in resources:
        our_d = cheb((sx, sy), (tx, ty))
        opp_d = cheb((ox, oy), (tx, ty))
        # If equal-time contest, slight preference to us (tie-break by smaller id).
        advantage = opp_d - our_d
        near_bias = -((tx + ty) % 3)  # deterministic small bias
        priority = advantage * 10 + near_bias - our_d * 0.1
        ranked.append((priority, tx, ty, our_d, opp_d))
    ranked.sort(reverse=True)

    top_targets = ranked[:6]

    best_move = (0, 0)
    best_score = None
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inside(nx, ny):
            continue
        score = 0.0
        # Evaluate: how much closer we get vs opponent on best contested targets.
        for i, (pri, tx, ty, _, _) in enumerate(top_targets):
            our_dn = cheb((nx, ny), (tx, ty))
            opp_dn = cheb((ox, oy), (tx, ty))
            # Encourage taking uncontested leads strongly; reduce if we fall behind.
            lead = opp_dn - our_dn
            score += (lead * (3.0 - 0.4 * i)) - 0.15 * our_dn
            # Minor obstacle-avoidance by discouraging stepping near obstacles.
            if any((nx + ax, ny + ay) in obs_cells for ax in (-1, 0, 1) for ay in (-1, 0, 1) if not (ax == 0 and ay == 0)):
                score -= 0.6
        # Deterministic tie-break: prefer staying closer to center-ish.
        cx, cy = w // 2, h // 2
        center = -(abs(nx - cx) + abs(ny - cy)) * 0.01
        score += center

        if best_score is None or score > best_score or (score == best_score and (dx, dy) < best_move):
            best_score = score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]