def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position", [0, 0]) or [0, 0]
    op = observation.get("opponent_position", [0, 0]) or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for r in observation.get("resources") or []:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    if not resources:
        return [0, 0]

    def dist(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    def cell_score(cx, cy):
        sd = dist((sx, sy), (cx, cy))
        od = dist((ox, oy), (cx, cy))
        # Prefer being closer; if opponent is closer, still prefer states that reduce that gap.
        lead = od - sd
        # Slightly prefer mid-board resources to avoid stalling on dead ends.
        center = -0.02 * (abs(cx - (w - 1) / 2) + abs(cy - (h - 1) / 2))
        return (lead, -sd, center)

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    best = None
    best_mv = (0, 0)

    # Pick a target deterministically: highest lead for our current position.
    target = max(resources, key=lambda c: cell_score(c[0], c[1]))

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h):
            continue
        if (nx, ny) in obstacles:
            continue

        # Evaluate by (1) progress to our best target, (2) denial on the resources opponent is near.
        my_d_t = dist((nx, ny), target)
        my_d_now = dist((sx, sy), target)

        # Denial: look at up to 3 closest resources to opponent and maximize our advantage after move.
        opp_candidates = sorted(resources, key=lambda c: dist((ox, oy), c))[:3]
        deny = 0
        for c in opp_candidates:
            sd = dist((nx, ny), c)
            od = dist((ox, oy), c)
            # If we can become closer than opponent, this is great; otherwise reduce their lead.
            deny = max(deny, (od - sd))

        # Combine: primarily go toward target; secondarily improve denial and avoid giving opponent too much lead.
        # Also nudge to not move away from target when deny is tie.
        val = (-(my_d_t), (my_d_now - my_d_t), deny, -abs(nx - ox) - abs(ny - oy), -nx - ny)
        if best is None or val > best:
            best = val
            best_mv = (dx, dy)

    return [int(best_mv[0]), int(best_mv[1])]