def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    gw = observation.get("grid_width", 8)
    gh = observation.get("grid_height", 8)
    resources = observation.get("resources", []) or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))

    if not resources:
        return [0, 0]

    deltas = [(-1, -1), (-1, 0), (-1, 1),
              (0, -1), (0, 0), (0, 1),
              (1, -1), (1, 0), (1, 1)]

    def man(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    # Pick a target deterministically: maximize advantage (opponent far, we close).
    best = None  # (key, tx, ty)
    for rx, ry in resources:
        ds = man(sx, sy, rx, ry)
        do = man(ox, oy, rx, ry)
        adv = do - ds
        # Prefer higher advantage; tie-break by smaller ds then coordinates.
        key = (-adv, ds, rx, ry)
        if best is None or key < best[0]:
            best = (key, rx, ry)

    _, tx, ty = best

    # Evaluate next moves: prioritize moving closer to target, while preventing immediate opponent capture.
    best_move = (10**9, 0, 0)  # (score, dx, dy)
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < gw and 0 <= ny < gh):
            continue
        if (nx, ny) in obstacles:
            continue

        ds_next = man(nx, ny, tx, ty)
        ds_cur = man(sx, sy, tx, ty)
        progress = ds_cur - ds_next  # positive is good

        # If opponent can reach some resource very soon from their current pos, try to reduce their advantage there.
        worst_pen = 0
        for rx, ry in resources:
            do = man(ox, oy, rx, ry)
            if do <= ds_cur + 2:  # contested-ish
                dp = man(nx, ny, rx, ry)
                worst_pen = min(worst_pen, (dp - do))  # smaller dp-do means we're closer than opponent
        # Convert penalty into reward: we want worst_pen to be as large as possible.
        # If worst_pen is very negative, we are still behind someone => penalize.
        contest_reward = worst_pen

        # Also avoid stepping into squares that are exactly equal to opponent's distance to the chosen target (likely contest tie).
        tie_pen = 0
        if man(nx, ny, tx, ty) == man(ox, oy, tx, ty):
            tie_pen = 1

        score = (-progress, -contest_reward, tie_pen, nx, ny)
        if score < best_move:
            best_move = (score, dx, dy)

    return [best_move[1], best_move[2]]