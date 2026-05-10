def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    resources = observation.get("resources", []) or []
    obstacles_list = observation.get("obstacles", []) or []
    obstacles = set()
    for p in obstacles_list:
        if p is not None and len(p) >= 2:
            obstacles.add((p[0], p[1]))

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def ok(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def man(a, b, c, d):
        return abs(a - c) + abs(b - d)

    if not resources:
        return [0, 0]

    # Sweep-row nemesis heuristic: block likely lanes by preferring targets on/near our next row step
    # and that reduce opponent's ability to reach them sooner.
    best = [0, 0]
    bestv = -10**18
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not ok(nx, ny):
            continue

        step_pen = 0
        if (nx, ny) in obstacles:
            step_pen = -1000

        # Prefer safe progress: avoid staying if any improving move exists.
        stay_pen = -2 if (dx == 0 and dy == 0) else 0

        v = stay_pen + step_pen
        lane_bias = 0
        # If we are changing row, consider that opponent tends to sweep; prioritize resources near our row trajectory.
        lane_bias = 1 if dy != 0 else 0

        # Evaluate against all resources using a deterministic aggregate
        # (maximize worst-case advantage to reduce competition surprises).
        worst = 10**18
        for r in resources:
            rx, ry = r[0], r[1]
            my_d = man(nx, ny, rx, ry)
            opp_d = man(ox, oy, rx, ry)
            adv = opp_d - my_d  # positive is good
            # Extra lane penalty/bonus: if opponent is on same row/col neighborhood, treat it as contested.
            contested = 0
            if abs(oy - ry) <= 0:
                contested = 2
            if abs(ox - rx) <= 0:
                contested += 1
            # Prefer nearer resources for earlier capture
            near = -0.15 * my_d
            # Prefer moving toward resources that also lie roughly in opponent sweep direction (row-like)
            row_alignment = -0.05 * abs(ny - ry) + 0.02 * (1 if ny == ry else 0)

            score = adv + near + row_alignment - contested + lane_bias
            if score < worst:
                worst = score
        v += worst
        # Small deterministic tie-break: favor moves with lexicographically smaller (dx,dy) among equals
        if v > bestv or (v == bestv and (dx, dy) < (best[0], best[1])):
            bestv = v
            best = [dx, dy]
    return [int(best[0]), int(best[1])]