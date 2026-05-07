def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w = int(observation["grid_width"])
    h = int(observation["grid_height"])
    resources = observation.get("resources") or []
    obstacles = observation.get("obstacles") or []

    obs = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obs.add((x, y))

    res_set = set()
    for r in resources:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h:
                res_set.add((x, y))

    def ok(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obs

    def md(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx + dy

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best_move = [0, 0]
    best_score = -10**18

    res_list = list(res_set)
    res_list.sort()
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not ok(nx, ny):
            continue

        immediate = 1 if (nx, ny) in res_set else 0
        # Evaluate "steal potential": prefer resources we reach not later than opponent.
        target_score = 0
        if res_list:
            cand = []
            for rx, ry in res_list:
                if (rx, ry) in obs:
                    continue
                d_ours = md(nx, ny, rx, ry)
                d_opp = md(ox, oy, rx, ry)
                lead = d_opp - d_ours  # positive if we are closer
                # Encourage closeness and having a lead; penalize being behind.
                score = lead * 5 - d_ours + (3 if (rx, ry) == (nx, ny) else 0)
                cand.append((score, -d_ours, lead, rx, ry))
            cand.sort(reverse=True)
            target_score = cand[0][0] if cand else 0

        # Small tie-breaker: move towards center to reduce dead-ends in open maps.
        cx, cy = (w - 1) / 2.0, (h - 1) / 2.0
        center_bias = -0.01 * (md(nx, ny, cx, cy) if isinstance(cx, float) else md(nx, ny, int(cx), int(cy)))

        score = immediate * 100 + target_score + center_bias
        if score > best_score:
            best_score = score
            best_move = [dx, dy]

    return best_move