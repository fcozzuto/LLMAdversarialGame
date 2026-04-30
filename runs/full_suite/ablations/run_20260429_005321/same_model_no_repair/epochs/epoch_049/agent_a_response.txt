def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    gw = observation.get("grid_width", 8)
    gh = observation.get("grid_height", 8)
    resources = observation.get("resources") or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles") or []))

    def king_dist(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def free(x, y):
        return 0 <= x < gw and 0 <= y < gh and (x, y) not in obstacles

    if not resources:
        return [0, 0]

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    opp_best_res = None
    best_opp = -10**18
    for rx, ry in resources:
        sd = king_dist(sx, sy, rx, ry)
        od = king_dist(ox, oy, rx, ry)
        v = (od - sd) * 60 - sd
        if v > best_opp:
            best_opp = v
            opp_best_res = (rx, ry)

    # Choose our main target: where we can beat opponent soonest; if none, just minimize their advantage.
    our_target = None
    best_my = -10**18
    for rx, ry in resources:
        sd = king_dist(sx, sy, rx, ry)
        od = king_dist(ox, oy, rx, ry)
        adv = od - sd  # positive favors us
        v = adv * 120 - sd * 2
        # Prefer resources with higher "win-likelihood" for us deterministically.
        if adv > 0:
            v += 500 - sd * 5
        if v > best_my:
            best_my = v
            our_target = (rx, ry)

    tx, ty = our_target
    dxo, dyo = opp_best_res

    best_move = (0, 0)
    best_score = -10**18
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not free(nx, ny):
            continue

        ds = king_dist(nx, ny, tx, ty)
        do = king_dist(ox, oy, tx, ty)

        # Primary: improve our capture race.
        score = (do - ds) * 140 - ds * 3

        # Secondary: deny opponent's likely target (increase their distance; don't help them).
        ds2 = king_dist(nx, ny, dxo, dyo)
        do2 = king_dist(ox, oy, dxo, dyo)
        score += (do2 - (do2 if ds2 < do2 else ds2)) * 40  # small penalty if we move toward their target

        # Micro-avoid ending at same cell as opponent (minor, deterministic).
        if nx == ox and ny == oy:
            score -= 50

        # Deterministic tie-break: prefer staying centered (roughly) then smaller dx,dy ordering.
        center_bias = -((gw - 1) / 2 - nx) ** 2 - ((gh - 1) / 2 - ny) ** 2
        score += center_bias * 0.001

        if score > best_score:
            best_score = score
            best_move = (dx, dy)

    return [best_move[0], best_move[1]]