def choose_move(observation):
    W = observation.get("grid_width", 8)
    H = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    resources = observation.get("resources", []) or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))

    def inb(x, y):
        return 0 <= x < W and 0 <= y < H

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    if not moves:
        return [0, 0]

    # Pick a target resource deterministically by best current advantage
    if resources:
        best = None
        for rx, ry in resources:
            myd = cheb(sx, sy, rx, ry)
            opd = cheb(ox, oy, rx, ry)
            adv = opd - myd
            key = (-adv, myd, rx, ry)  # maximize adv; then minimize myd; then lexicographic
            if best is None or key < best[0]:
                best = (key, rx, ry)
        tx, ty = best[1], best[2]
    else:
        tx, ty = (W - 1) // 2, (H - 1) // 2

    best_move = (0, 0)
    best_score = -10**18
    # Evaluate local moves with respect to best available advantage and opponent distance
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue

        if resources:
            # Compute best advantage over resources from next position
            best_adv = -10**9
            best_myd = 10**9
            for rx, ry in resources:
                dmy = cheb(nx, ny, rx, ry)
                dop = cheb(ox, oy, rx, ry)
                adv = dop - dmy
                if adv > best_adv or (adv == best_adv and (dmy < best_myd or (dmy == best_myd and (rx, ry) < (tx, ty)))):
                    best_adv = adv
                    best_myd = dmy
            # Encourage getting closer to the chosen target as a tiebreak
            d_to_target = cheb(nx, ny, tx, ty)
            # Small penalty for getting too close to opponent (avoid useless fighting)
            opp_d = cheb(nx, ny, ox, oy)
            score = best_adv * 100 + (-d_to_target) * 2 + opp_d * 0.05
        else:
            score = -cheb(nx, ny, tx, ty)

        # Deterministic tie-break: prefer smaller (dx,dy) in moves order
        if score > best_score:
            best_score = score
            best_move = (dx, dy)
    return [int(best_move[0]), int(best_move[1])]