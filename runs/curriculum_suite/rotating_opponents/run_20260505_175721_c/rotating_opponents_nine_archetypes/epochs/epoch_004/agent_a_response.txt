def choose_move(observation):
    w = observation.get("grid_width", 8) or 8
    h = observation.get("grid_height", 8) or 8
    sp = observation.get("self_position", (0, 0)) or (0, 0)
    op = observation.get("opponent_position", (0, 0)) or (0, 0)
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))
    resources = observation.get("resources", []) or []

    def dist(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    def best_target():
        if not resources:
            return w // 2, h // 2
        # Prefer resources where we are closer than opponent; if none, chase nearest overall.
        best = None
        best_key = None
        for rx, ry in resources:
            myd = dist(sx, sy, rx, ry)
            opd = dist(ox, oy, rx, ry)
            adv = opd - myd  # positive means we are closer
            # Key: maximize advantage -> minimize negative advantage; then closer to us; then stable ordering
            key = (-adv, myd, rx, ry)
            if best_key is None or key < best_key:
                best_key = key
                best = (rx, ry, adv, myd, opd)
        return best[0], best[1]

    tx, ty = best_target()

    # If opponent is already adjacent to our chosen target, try to move to a square that increases their distance.
    opp_adj = dist(ox, oy, tx, ty) <= 1

    best_move = (0, 0)
    best_score = None

    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            if nx < 0 or nx >= w or ny < 0 or ny >= h:
                continue
            if (nx, ny) in obstacles:
                continue
            d_to_t = dist(nx, ny, tx, ty)
            d_to_o = dist(nx, ny, ox, oy)

            # Base: get closer to target, while not letting opponent get closer to the target.
            opp_d_curr = dist(ox, oy, tx, ty)
            opp_d_next = dist(nx, ny, tx, ty)  # used only for opponent proxy below

            # Opponent proxy: compare who can reach target sooner from candidate.
            myd_next = dist(nx, ny, tx, ty)
            opd_curr = dist(ox, oy, tx, ty)

            # Score components
            score = 0
            score += -d_to_t * 3
            score += d_to_o * 0.5
            score += (opd_curr - myd_next) * 2  # positive if we improve relative access

            if opp_adj:
                # Urge to increase distance from opponent and reduce chance they step onto target.
                score += (d_to_o) * 2
                score += -abs(d_to_t - opp_d_curr)

            # Deterministic tie-break: prefer straight moves over diagonals, then lexicographic dx,dy
            diag_pen = 1 if dx != 0 and dy != 0 else 0
            score_key = (-score, diag_pen, dx, dy, nx, ny)

            if best_score is None or score_key < best_score:
                best_score = score_key
                best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]