def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", []) or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    legal = []
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            if inb(nx, ny) and (nx, ny) not in obstacles:
                legal.append((dx, dy))
    if not legal:
        return [0, 0]

    if not resources:
        dx = 1 if ox > sx else (-1 if ox < sx else 0)
        dy = 1 if oy > sy else (-1 if oy < sy else 0)
        return [dx, dy]

    res_list = [tuple(r) for r in resources]
    # deterministic tie-break: prefer lower x then y
    res_list.sort()

    def dist(ax, ay, bx, by):
        return abs(ax - bx) + abs(ay - by)

    opp_corner_pref = (ox < w - 1) - (ox > 0)  # sign for pushing x towards opponent
    best = None  # (score, dx, dy)
    for dx, dy in legal:
        nx, ny = sx + dx, sy + dy
        on_resource = (nx, ny) in obstacles and False  # no-op; obstacles already filtered
        if (nx, ny) in set(res_list):
            # strong immediate gain
            return [dx, dy]

        best_gap = -10**9
        best_tb = None
        best_dme = None
        for rx, ry in res_list:
            d_me = dist(nx, ny, rx, ry)
            d_op = dist(ox, oy, rx, ry)
            gap = d_op - d_me
            tb = -(rx * 8 + ry)  # prefer "earlier" cells consistently
            if gap > best_gap or (gap == best_gap and (d_me < best_dme or (d_me == best_dme and tb > best_tb))):
                best_gap = gap
                best_tb = tb
                best_dme = d_me

        # Also slightly encourage moving towards our next target and away from being stuck
        # (penalize staying if it doesn't improve distance advantage).
        stay_pen = 0
        if dx == 0 and dy == 0:
            stay_pen = 0.5

        # small directional nudge to prevent cycling: drift toward better quadrant relative to opponent
        nudge = 0
        if opp_corner_pref != 0:
            nudge = 0.01 * (nx - sx) * opp_corner_pref

        score = best_gap * 1000 - (best_dme if best_dme is not None else 0) - stay_pen + nudge
        if best is None or score > best[0]:
            best = (score, dx, dy)

    return [int(best[1]), int(best[2])]