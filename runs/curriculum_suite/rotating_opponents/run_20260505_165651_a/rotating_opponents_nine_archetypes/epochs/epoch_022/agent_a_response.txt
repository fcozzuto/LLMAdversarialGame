def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    resources = observation.get("resources") or []
    obs = set(tuple(p) for p in (observation.get("obstacles") or []))
    if not resources:
        return [0, 0]

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obs

    def king_dist(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    # Prefer moves that maximize guaranteed "capture advantage" on at least one resource.
    # Deterministic tie-break: higher advantage, then lower best my-distance, then lower opponent-distance,
    # then lexicographically smallest move.
    best_move = (0, 0)
    best_key = (-10**18, 10**18, 10**18, -10**18)  # (adv, -myd, -oppd, -(stay penalty))

    for dxm, dym in moves:
        nx, ny = sx + dxm, sy + dym
        if not inb(nx, ny):
            continue

        best_adv = -10**18
        best_myd = 10**18
        best_oppd = 10**18

        for rx, ry in resources:
            myd = king_dist(nx, ny, rx, ry)
            oppd = king_dist(ox, oy, rx, ry)
            adv = oppd - myd
            if adv > best_adv or (adv == best_adv and (myd < best_myd or (myd == best_myd and oppd < best_oppd))):
                best_adv, best_myd, best_oppd = adv, myd, oppd

        # Encourage progress (slight) and avoid wasting by staying if not locally best.
        stay_pen = -1 if (dxm == 0 and dym == 0) else 0
        key = (best_adv, -best_myd, -best_oppd, stay_pen)
        if key > best_key or (key == best_key and (dxm, dym) < best_move):
            best_key = key
            best_move = (dxm, dym)

    return [int(best_move[0]), int(best_move[1])]