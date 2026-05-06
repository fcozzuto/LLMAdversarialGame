def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    resources = observation.get("resources") or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles") or []))
    if not resources:
        return [0, 0]

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def king_dist(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    # Choose move that maximizes the best "capture advantage" over the opponent:
    # for some resource r, (opp_dist_to_r - my_dist_to_r). Tie-break by reaching sooner (my_dist),
    # then by keeping closer to the opponent (to avoid them stealing alternatives).
    best = [0, 0]
    best_val = -10**18

    for dxm, dym in moves:
        nx, ny = sx + dxm, sy + dym
        if not inb(nx, ny):
            continue

        best_adv = -10**18
        best_myd = 10**18
        best_opp_myd = 10**18
        for rx, ry in resources:
            myd = king_dist(nx, ny, rx, ry)
            oppd = king_dist(ox, oy, rx, ry)
            adv = oppd - myd
            if adv > best_adv or (adv == best_adv and myd < best_myd) or (adv == best_adv and myd == best_myd and oppd < best_opp_myd):
                best_adv = adv
                best_myd = myd
                best_opp_myd = oppd

        # Small deterministic bias: prefer diagonal moves if equally good.
        diag_bonus = 0 if (dxm == 0 or dym == 0) else 0.01

        # Extra pressure: if we can tie-advance (adv >= 0), strongly prefer those.
        tie_pressure = 0
        if best_adv >= 0:
            tie_pressure = 0.5 * best_adv

        val = best_adv * 100 + tie_pressure - best_myd + diag_bonus
        if val > best_val:
            best_val = val
            best = [dxm, dym]

    return best