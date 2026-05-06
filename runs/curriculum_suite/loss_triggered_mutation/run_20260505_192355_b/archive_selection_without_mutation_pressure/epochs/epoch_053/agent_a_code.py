def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sp = observation.get("self_position", [0, 0])
    op = observation.get("opponent_position", [0, 0])
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    resources = observation.get("resources") or []
    if not resources:
        return [0, 0]
    obstacles = set((int(p[0]), int(p[1])) for p in (observation.get("obstacles") or []))

    def ok(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def manh(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0:
            dx = -dx
        dy = y1 - y2
        if dy < 0:
            dy = -dy
        return dx + dy

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    # Avoid mirroring "nearest resource" by favoring resources where we can create or expand a distance advantage,
    # while also nudging toward resources that have "low opponent pressure".
    best_score = -10**18
    best_move = (0, 0)
    res_list = [(int(r[0]), int(r[1])) for r in resources]

    for dxm, dym in moves:
        nx, ny = sx + dxm, sy + dym
        if not ok(nx, ny):
            continue

        score = 0.0
        nearest_self = 10**9
        nearest_opp = 10**9

        for rx, ry in res_list:
            sd = manh(nx, ny, rx, ry)
            od = manh(ox, oy, rx, ry)
            if sd < nearest_self:
                nearest_self = sd
            if od < nearest_opp:
                nearest_opp = od

            # Distance-advantage core
            adv = od - sd  # positive means we're closer to that resource
            # Interference pressure: if opponent is already much closer, deprioritize unless we can flip.
            flip = 1 if sd <= od else 0
            pressure = (od - sd) if od < sd else 0  # non-positive normally; penalize only when opponent is closer
            score += 2.2 * adv + 0.9 * flip - 0.08 * sd + 0.03 * pressure

        # Anti-stagnation: prefer moves that reduce our nearest distance when it doesn't sacrifice advantage.
        score += 0.06 * (nearest_opp - nearest_self)

        # Slight tie-breaker toward moving in the direction of the best current target.
        if score > best_score:
            best_score = score
            best_move = (dxm, dym)

    return [int(best_move[0]), int(best_move[1])]