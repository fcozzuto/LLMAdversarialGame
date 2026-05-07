def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources") or []
    obstacles = observation.get("obstacles") or []
    obs = set(map(tuple, obstacles))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def dist(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    if not resources:
        return [0, 0]

    # pick a deterministic "focus" target near where we are currently advantaged
    best_focus = None
    best_val = -10**9
    for r in resources:
        sd = abs(r[0] - sx) + abs(r[1] - sy)
        od = abs(r[0] - ox) + abs(r[1] - oy)
        val = (od - sd) * 10 - sd
        if val > best_val:
            best_val = val
            best_focus = r
    if best_focus is None:
        best_focus = resources[0]

    # avoid opponent by aiming for focus, but if opponent is much closer to focus, switch focus deterministically
    fs_sd = abs(best_focus[0] - sx) + abs(best_focus[1] - sy)
    fs_od = abs(best_focus[0] - ox) + abs(best_focus[1] - oy)
    if fs_od + 1 < fs_sd and len(resources) > 1:
        # choose a resource where we are closest relative to opponent
        best_focus2 = best_focus
        best_val2 = -10**9
        for r in resources:
            sd = abs(r[0] - sx) + abs(r[1] - sy)
            od = abs(r[0] - ox) + abs(r[1] - oy)
            val = (od - sd) * 12 - sd
            if val > best_val2:
                best_val2 = val
                best_focus2 = r
        best_focus = best_focus2

    # evaluate each possible next cell using a minimax-like immediate advantage over all resources
    best_move = [0, 0]
    best_score = -10**18
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obs:
            continue
        my_pos = (nx, ny)

        worst_case = 10**9
        best_case = -10**9
        for r in resources:
            sd = dist(my_pos, r)
            od = dist((ox, oy), r)
            advantage = od - sd  # higher is better
            if advantage < worst_case:
                worst_case = advantage
            if advantage > best_case:
                best_case = advantage

        # blend: prioritize secure advantage, then prefer getting close to focus
        focus_d = dist(my_pos, best_focus)
        opp_to_focus = dist((ox, oy), best_focus)
        score = (worst_case * 20) + (best_case) - focus_d - (max(0, focus_d - opp_to_focus) * 3)

        if score > best_score:
            best_score = score
            best_move = [dx, dy]

    return best_move