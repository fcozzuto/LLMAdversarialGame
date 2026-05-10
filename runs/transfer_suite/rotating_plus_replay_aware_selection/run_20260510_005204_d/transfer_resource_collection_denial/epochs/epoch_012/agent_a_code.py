def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", []) or []
    obs_list = observation.get("obstacles", []) or []
    obstacles = set((p[0], p[1]) for p in obs_list)

    def inside(x, y):
        return 0 <= x < w and 0 <= y < h

    def dist(a, b, c, d):
        dx = a - c
        if dx < 0: dx = -dx
        dy = b - d
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def cell_score(x, y, rx, ry, step_to_target):
        # Prefer short path to target, strongly avoid being blocked by obstacles
        if (x, y) in obstacles:
            return -10**9
        base = -step_to_target - 0.15 * (abs(rx - (w - 1) / 2) + abs(ry - (h - 1) / 2))
        # Penalty if near obstacles (discourage risky moves)
        p = 0
        for ax in (-1, 0, 1):
            for ay in (-1, 0, 1):
                if ax == 0 and ay == 0:
                    continue
                nx, ny = x + ax, y + ay
                if (nx, ny) in obstacles:
                    p += 1
        return base - 0.35 * p

    if not resources:
        return [0, 0]

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best_move = (0, 0)
    best_val = -10**18

    # Choose target by "capture advantage": how much closer we are than opponent
    best_targets = []
    for rx, ry in resources:
        myd = dist(sx, sy, rx, ry)
        opd = dist(ox, oy, rx, ry)
        adv = opd - myd
        # Slightly prefer resources with lower opponent reach even if not best adv
        center_bias = -abs(rx - (w - 1) / 2) - abs(ry - (h - 1) / 2)
        best_targets.append((adv, center_bias, rx, ry, myd, opd))
    best_targets.sort(reverse=True)
    best_targets = best_targets[:5]

    # If opponent is close to any resource we could deny, weight that denial higher
    deny_targets = []
    for adv, cb, rx, ry, myd, opd in best_targets:
        if opd <= myd + 1:
            deny_targets.append((opd, rx, ry))
    deny_targets.sort()

    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not inside(nx, ny):
            continue
        # If move hits obstacle, engine keeps us in place; still allow but score should reflect risk
        val = 0.0

        # Main objective: progress toward best capture target
        for adv, cb, rx, ry, myd, opd in best_targets:
            d_to = dist(nx, ny, rx, ry)
            # advantage after move
            my_adv = opd - d_to
            val += 6.0 * my_adv + cell_score(nx, ny, rx, ry, d_to) + 0.2 * cb

        # Secondary: denial pressure (move toward resources opponent is also reaching)
        for opd, rx, ry in deny_targets[:2]:
            d_to = dist(nx, ny, rx, ry)
            # If we can keep them from being closest next, that's good
            val += 4.0 * (d_to - opd) * -1  # prefer being not worse than opponent

        # Small tie-break toward moving generally away from center? no—toward closer
        val -= 0.02 * (abs(nx - (w - 1) / 2) + abs(ny - (h - 1) / 2))

        # Avoid stepping directly onto obstacle (big penalty)
        if (nx, ny) in obstacles:
            val -= 1e6

        if val > best_val:
            best_val = val
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]