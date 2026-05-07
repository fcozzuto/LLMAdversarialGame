def choose_move(observation):
    w = observation["grid_width"]; h = observation["grid_height"]
    sx, sy = observation["self_position"]; ox, oy = observation["opponent_position"]
    resources = observation.get("resources") or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles") or []))
    if not resources:
        return [0, 0]

    scores = observation.get("scores") or {}
    self_name = observation.get("self_name")
    opp_name = observation.get("opponent_name")
    my_score = scores.get(self_name, 0.0)
    opp_score = scores.get(opp_name, 0.0)
    leading = my_score >= opp_score

    def man(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx + dy

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    best = (-10**18, 0, 0)
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h):
            continue
        if (nx, ny) in obstacles:
            continue

        adj = 0
        for obx, oby in obstacles:
            if man(nx, ny, obx, oby) == 1:
                adj += 1

        # Resource evaluation: prefer high opponent-minus-self distance when contesting,
        # otherwise prefer low self distance (and still avoid giving opponent easy access).
        if leading:
            focus = 1  # self-first
        else:
            focus = 0  # contest-first

        best_res = -10**18
        min_my = 10**9
        min_op = 10**9
        for rx, ry in resources:
            myd = man(nx, ny, rx, ry)
            opd = man(ox, oy, rx, ry)
            if myd < min_my: min_my = myd
            if opd < min_op: min_op = opd
            if focus:
                val = (-myd) * 10 + (opd - myd)
            else:
                val = (opd - myd) * 10 - myd
            # If we're closer than opponent, strongly prefer that resource.
            if myd < opd:
                val += 50
            best_res = val if val > best_res else best_res

        # Minor shaping: keep moving away from being adjacent to obstacles.
        # Also small tie-break toward reducing opponent's nearest distance.
        opponent_push = -min_op
        own_push = -min_my
        val = best_res + opponent_push * 0.1 + own_push * 0.01 - adj * 0.5

        if val > best[0]:
            best = (val, dx, dy)

    return [best[1], best[2]]