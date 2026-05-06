def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    resources = observation.get("resources") or []
    obstacles = observation.get("obstacles") or []

    obs = set()
    for o in obstacles:
        if isinstance(o, (list, tuple)) and len(o) == 2:
            x, y = o[0], o[1]
            if isinstance(x, int) and isinstance(y, int) and 0 <= x < w and 0 <= y < h:
                obs.add((x, y))

    res = []
    for r in resources:
        if isinstance(r, (list, tuple)) and len(r) == 2:
            x, y = r[0], r[1]
            if isinstance(x, int) and isinstance(y, int) and 0 <= x < w and 0 <= y < h and (x, y) not in obs:
                res.append((x, y))
    if not res:
        return [0, 0]

    def md(ax, ay, bx, by):
        return abs(ax - bx) + abs(ay - by)

    # Opponent's current best resource (for blocking)
    opp_target = min(res, key=lambda p: (md(ox, oy, p[0], p[1]), p[0], p[1]))
    txo, tyo = opp_target

    deltas = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    best = None
    best_score = -10**18

    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if nx < 0 or nx >= w or ny < 0 or ny >= h or (nx, ny) in obs:
            continue

        score = 0
        # local positional preference: keep closer to center-ish and reduce distance between agents (intercept)
        midx, midy = (w - 1) / 2.0, (h - 1) / 2.0
        score += -0.05 * (abs(nx - midx) + abs(ny - midy))
        score += -0.02 * (md(nx, ny, ox, oy))

        # resource race / stealing pressure
        for tx, ty in res:
            myd = md(nx, ny, tx, ty)
            opd = md(ox, oy, tx, ty)
            # prefer resources where we are closer than opponent; strongly punish where we fall behind
            score += 10.0 * (opd - myd) - 0.25 * myd
            # extra shaping for the opponent's nearest target: try to become the new closest
            if tx == txo and ty == tyo:
                # approximate opponent next advantage by assuming opponent moves 1 step toward that target
                opd_next = max(0, opd - 1)
                myd_next = max(0, myd - 1)
                score += 40.0 * ((opd_next - myd_next) - 0.3)  # encourage overtaking/intercept

        # if we can directly step closer to opp_target, add a small deterministic boost
        if md(nx, ny, txo, tyo) < md(sx, sy, txo, tyo):
            score += 8.0

        # tie-break deterministically: prefer smaller dx, then smaller dy, then straight-ish moves
        tie = (score, -abs(dx) - abs(dy), -abs(dx), -abs(dy), dx, dy)
        if best is None or tie > best:
            best = tie
            best_score = score
            best_move = [dx, dy]

    if best is None:
        return [0, 0]
    return best_move