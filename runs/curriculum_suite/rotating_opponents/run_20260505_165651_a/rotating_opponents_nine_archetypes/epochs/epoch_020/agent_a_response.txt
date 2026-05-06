def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    resources = observation.get("resources") or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles") or []))
    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    if not resources:
        return [0, 0]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def king_dist(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    opp_target = min(resources, key=lambda r: king_dist(ox, oy, r[0], r[1]))
    oxr, oyr = opp_target[0], opp_target[1]

    best_move = [0, 0]
    best_score = -10**9

    for dxm, dym in moves:
        nx, ny = sx + dxm, sy + dym
        if not inb(nx, ny):
            continue

        my_dist_to_target = king_dist(nx, ny, oxr, oyr)

        # Choose the resource where we can most beat the opponent (reach earlier),
        # else fall back to minimizing our distance to opponent-most-likely target.
        best_adv = -10**9
        best_myd = 10**9
        for rx, ry in resources:
            myd = king_dist(nx, ny, rx, ry)
            oppd = king_dist(ox, oy, rx, ry)
            adv = oppd - myd
            if adv > best_adv or (adv == best_adv and myd < best_myd):
                best_adv = adv
                best_myd = myd

        # Encourage taking wins (adv>0) and blocking opponent by drifting away from
        # their likely path to the same target.
        score = 6 * best_adv - 0.8 * my_dist_to_target + (-0.05) * best_myd
        if score > best_score:
            best_score = score
            best_move = [dxm, dym]

    return [int(best_move[0]), int(best_move[1])]