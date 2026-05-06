def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0])[:2]
    ox, oy = observation.get("opponent_position", [0, 0])[:2]
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obs = set()
    for p in observation.get("obstacles", []) or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obs.add((x, y))

    resources = []
    for p in observation.get("resources", []) or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obs:
                resources.append((x, y))

    if not resources:
        return [0, 0]

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    cx, cy = w // 2, h // 2

    def blocked(nx, ny):
        return not (0 <= nx < w and 0 <= ny < h) or (nx, ny) in obs

    def man(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    # Choose a move by "racing" resources the opponent can reach soon, but only if we can beat them.
    best = (0, 0)
    best_val = -10**18
    my_pos = (sx, sy)
    opp_pos = (ox, oy)

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if blocked(nx, ny):
            nx, ny = sx, sy
        new_pos = (nx, ny)

        self_center_bias = -0.01 * man(new_pos, (cx, cy))
        val = self_center_bias

        # Evaluate only the most "contested" few resources for speed + determinism
        scored = []
        for r in resources:
            sd = man(new_pos, r)
            od = man(opp_pos, r)
            # Want resources where we are closer; also prioritize those opponent can contest quickly.
            # If we can't beat them, heavily penalize.
            adv = od - sd
            contested = -od
            race_score = 1000 * adv + 3 * contested - sd
            scored.append((race_score, adv, -od, sd, r))
        scored.sort(reverse=True)
        top = scored[:4]

        # Use max over top resources with a slight preference for higher sd tie-break to reduce dithering.
        local = top[0][0] if top else -10**18
        # If the best adv is not positive, still try to reduce opponent pressure by moving toward their closest threats.
        if top and top[0][1] <= 0:
            pressure = top[0][2]
            local = local - 200 * (top[0][1] - 0) + 0.5 * pressure

        val += local
        if val > best_val:
            best_val = val
            best = (nx - sx, ny - sy)

    bx, by = best
    if bx not in (-1, 0, 1) or by not in (-1, 0, 1):
        return [0, 0]
    return [bx, by]