def choose_move(observation):
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))

    obstacles = observation.get("obstacles") or []
    obs = set()
    for p in obstacles:
        try:
            x, y = p
            x, y = int(x), int(y)
            if 0 <= x < w and 0 <= y < h:
                obs.add((x, y))
        except Exception:
            pass

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def ok(x, y):
        return inb(x, y) and (x, y) not in obs

    res_list = observation.get("resources") or []
    resources = []
    for p in res_list:
        try:
            x, y = p
            x, y = int(x), int(y)
            if ok(x, y):
                resources.append((x, y))
        except Exception:
            pass

    if not ok(int(sx), int(sy)):
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                nx, ny = int(sx) + dx, int(sy) + dy
                if ok(nx, ny):
                    return [dx, dy]
        return [0, 0]

    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)
    if not resources:
        return [0, 0]

    def md(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    # Pick a resource where we have relative advantage; if none, pick nearest.
    best = None
    best_key = None
    for tx, ty in resources:
        sd = md(sx, sy, tx, ty)
        od = md(ox, oy, tx, ty)
        # Favor (we are closer than opp) and nearer overall; penalize being far.
        key = (od - sd, -(sd), -(tx == sx and ty == sy))
        if best_key is None or key > best_key:
            best_key = key
            best = (tx, ty)

    tx, ty = best

    # One-step greedy with obstacle-avoidance; tie-break by also reducing opponent closeness.
    deltas = [(dx, dy) for dx in (-1, 0, 1) for dy in (-1, 0, 1)]
    best_move = (0, 0)
    best_score = None
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not ok(nx, ny):
            continue
        my_d = md(nx, ny, tx, ty)
        opp_d = md(nx, ny, ox, oy)  # prefer moves that also keep pressure positioning
        # Opponent closeness to target if we move here:
        opp_to_target = md(ox, oy, tx, ty)
        score = (-my_d, opp_to_target, opp_d, -(abs(dx) + abs(dy)))
        if best_score is None or score > best_score:
            best_score = score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]