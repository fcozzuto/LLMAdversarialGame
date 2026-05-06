def choose_move(observation):
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    resources = observation.get("resources") or []
    obstacles = observation.get("obstacles") or []

    obs = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obs.add((x, y))

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def md(ax, ay, bx, by):
        return abs(ax - bx) + abs(ay - by)

    rlist = []
    for r in resources:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if inb(x, y) and (x, y) not in obs:
                rlist.append((x, y))
    if not rlist:
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if inb(nx, ny) and (nx, ny) not in obs:
                return [dx, dy]
        return [0, 0]

    # Pick a target that is relatively hard for opponent but closer for us.
    best_r = None
    best_val = None
    for rx, ry in rlist:
        so = md(ox, oy, rx, ry)
        ss = md(sx, sy, rx, ry)
        val = (so - ss, -so, -ss, -rx, -ry)  # lexicographic max via tuple
        if best_val is None or val > best_val:
            best_val = val
            best_r = (rx, ry)
    rx, ry = best_r

    # Move: reduce our distance to target; simultaneously increase opponent's distance to that target.
    best_m = None
    best_s = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obs:
            continue
        self_d = md(nx, ny, rx, ry)
        opp_d = md(ox, oy, rx, ry)
        # immediate position doesn't change opponent distance; use second term to discourage moves that help opponent elsewhere
        # by approximating their progress to any resource.
        opp_best = None
        for tx, ty in rlist:
            d = md(ox, oy, tx, ty)
            if opp_best is None or d < opp_best:
                opp_best = d
        # our move may reduce opponent incentive by increasing ours towards target while keeping opponent's nearest unchanged
        score = (-self_d, -opp_best, dx, dy)
        if best_s is None or score > best_s:
            best_s = score
            best_m = (dx, dy)
    if best_m is None:
        return [0, 0]
    return [int(best_m[0]), int(best_m[1])]