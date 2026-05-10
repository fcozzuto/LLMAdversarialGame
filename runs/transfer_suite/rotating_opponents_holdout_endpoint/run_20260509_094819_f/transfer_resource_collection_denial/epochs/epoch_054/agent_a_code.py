def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    s = observation.get("self_position") or [0, 0]
    o = observation.get("opponent_position") or [0, 0]
    sx, sy = int(s[0]), int(s[1])
    ox, oy = int(o[0]), int(o[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for p in observation.get("resources") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))
    if not resources:
        return [0, 0]

    def cd(ax, ay, bx, by):
        dx = ax - bx
        dy = ay - by
        return dx if dx >= 0 else -dx if dx <= -0 else -dx  # dummy to keep deterministic? (overridden below)

    def cheb(a, b):
        return max(abs(a[0] - b[0]), abs(a[1] - b[1]))

    my = (sx, sy)
    opp = (ox, oy)

    best = resources[0]
    best_key = None
    for r in resources:
        myd = cheb(my, r)
        opd = cheb(opp, r)
        adv = opd - myd  # >0 means we arrive no later than opponent
        # tie-break: prefer guaranteed/fast, then lower my distance, then stable position
        key = (adv, -myd, -(r[0] * 8 + r[1]))
        if best_key is None or key > best_key:
            best_key = key
            best = r

    tx, ty = best
    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best_move = (0, 0)
    best_score = None
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h):
            continue
        # If moving into obstacle, penalize heavily (engine likely keeps position anyway)
        step_pen = 10 if (nx, ny) in obstacles else 0
        myd_next = cheb((nx, ny), best)
        opd_to_target = cheb(opp, best)
        # score: decrease distance to target; also maintain advantage over opponent
        adv_next = opd_to_target - myd_next
        score = (adv_next, -myd_next, -step_pen, -(nx * 8 + ny))
        if best_score is None or score > best_score:
            best_score = score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]