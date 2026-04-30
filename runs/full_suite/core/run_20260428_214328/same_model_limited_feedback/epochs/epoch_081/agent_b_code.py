def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    obstacles = set((x, y) for x, y in observation.get("obstacles", []))
    resources = observation.get("resources", []) or []
    # Candidate moves
    moves = [(dx, dy) for dx in (-1, 0, 1) for dy in (-1, 0, 1)]
    if not resources:
        # Drift to center while avoiding obstacles
        tx, ty = w // 2, h // 2
        best = (10**9, 0, 0)
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if nx < 0 or ny < 0 or nx >= w or ny >= h or (nx, ny) in obstacles:
                continue
            d = abs(nx - tx) + abs(ny - ty)
            if d < best[0]:
                best = (d, dx, dy)
        return [best[1], best[2]] if best[0] != 10**9 else [0, 0]

    def man(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    # Select target resource we are relatively closer to
    best_res = None
    best_key = (-10**9, 10**9)  # (opp_d - self_d, -self_d)
    for r in resources:
        sd = man((sx, sy), r)
        od = man((ox, oy), r)
        key = (od - sd, -sd)
        if key > best_key:
            best_key = key
            best_res = r

    tx, ty = best_res
    # Evaluate moves deterministically
    best_score = -10**18
    best_move = (0, 0)
    # If opponent is closer to target, contest by moving toward opponent as secondary
    opp_closer = man((ox, oy), (tx, ty)) < man((sx, sy), (tx, ty))

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if nx < 0 or ny < 0 or nx >= w or ny >= h or (nx, ny) in obstacles:
            continue
        self_d = abs(nx - tx) + abs(ny - ty)

        # Prefer moving onto a resource position (exact match)
        on_resource = 1 if (nx, ny) in set((x, y) for x, y in resources) else 0

        # Contest if opponent is closer: reduce our distance to opponent; otherwise, keep distance
        d_opp_after = abs(nx - ox) + abs(ny - oy)
        d_opp_now = abs(sx - ox) + abs(sy - oy)
        contest_bonus = (d_opp_now - d_opp_after) if opp_closer else (d_opp_after - d_opp_now)

        # Also slightly repel from obstacles nearby (simple penalty)
        near_obs_pen = 0
        for ex, ey in obstacles:
            if abs(nx - ex) + abs(ny - ey) == 1:
                near_obs_pen += 1

        # Main score: minimize distance to target, maximize relative contest/advantage
        score = (-self_d * 10) + (on_resource * 500) + (contest_bonus * 2) - (near_obs_pen * 3)
        if score > best_score:
            best_score = score
            best_move = (dx, dy)

    return [best_move[0], best_move[1]]