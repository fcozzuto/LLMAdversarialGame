def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    resources = observation.get("resources", []) or []
    obstacles = {(p[0], p[1]) for p in (observation.get("obstacles", []) or [])}
    rem = observation.get("remaining_resource_count", len(resources))

    def inside(nx, ny):
        return 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles

    def md(ax, ay, bx, by):
        return abs(ax - bx) + abs(ay - by)

    if not resources:
        return [0, 0]

    # Pick a target emphasizing who can reach it first (resource_denier-friendly).
    best_targets = []
    for rx, ry in resources:
        sd = md(sx, sy, rx, ry)
        od = md(ox, oy, rx, ry)
        adv = od - sd  # positive means we're closer
        best_targets.append((adv, -sd, rx, ry))
    best_targets.sort(reverse=True)
    # If no advantage anywhere, fall back to nearest resource.
    adv0 = best_targets[0][0]
    if adv0 <= 0:
        best_targets.sort(key=lambda t: (t[1], -t[0], t[2], t[3]))
        _, _, tx, ty = best_targets[0]
    else:
        _, _, tx, ty = best_targets[0]

    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    cur_sd = md(sx, sy, tx, ty)
    cur_od = md(ox, oy, tx, ty)

    best_move = (0, 0)
    best_score = -10**18

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inside(nx, ny):
            nx, ny = sx, sy
        self_d = md(nx, ny, tx, ty)
        opp_d = md(ox, oy, tx, ty)

        # Bonus if collecting (on resource cell).
        on_res = (nx, ny) in {(p[0], p[1]) for p in resources}
        collect_bonus = 50 if on_res else 0

        # Main: advance toward target and deny opponent by increasing relative distance.
        # Secondary: avoid wasting steps when few resources remain.
        score = (cur_sd - self_d) * 3 + (opp_d - self_d) * 1.5
        score += collect_bonus
        score += (10 - rem) * (1 if on_res else 0)

        # Small tie-breaker: prefer moves that also increase distance from opponent's position.
        score += (md(nx, ny, ox, oy) - md(sx, sy, ox, oy)) * 0.1

        if score > best_score:
            best_score = score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]