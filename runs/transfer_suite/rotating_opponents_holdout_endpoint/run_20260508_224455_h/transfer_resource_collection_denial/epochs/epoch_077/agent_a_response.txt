def choose_move(observation):
    sx, sy = int(observation["self_position"][0]), int(observation["self_position"][1])
    ox, oy = int(observation["opponent_position"][0]), int(observation["opponent_position"][1])
    gw, gh = int(observation["grid_width"]), int(observation["grid_height"])
    resources = observation.get("resources") or []
    if not resources:
        return [0, 0]
    res = [(int(r[0]), int(r[1])) for r in resources]
    obstacles = {(int(p[0]), int(p[1])) for p in (observation.get("obstacles") or [])}

    def inb(x, y):
        return 0 <= x < gw and 0 <= y < gh

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    def dist(a, b):
        dx = a[0] - b[0]
        dy = a[1] - b[1]
        return (dx if dx >= 0 else -dx) + (dy if dy >= 0 else -dy)

    Rset = set(res)
    best_move = [0, 0]
    best_val = -10**18

    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue
        # Prefer immediate collection
        if (nx, ny) in Rset:
            val = 10**12 + (sx - nx) * 0  # deterministic
            # still discourage walking into a cell adjacent to obstacle? keep simple
            if val > best_val:
                best_val = val
                best_move = [dx, dy]
            continue

        my_to = 10**18
        opp_to = 10**18
        # Choose target via contest-aware score: we want resources where we can arrive not worse than opponent.
        # Score move by best target for us among all resources.
        for rx, ry in res:
            myd = dist((nx, ny), (rx, ry))
            opd = dist((ox, oy), (rx, ry))
            # Higher is better: prioritize smaller myd, larger lead over opponent, and also overall availability.
            # If opponent already much closer, downweight this target.
            lead = opd - myd  # positive means we are closer than opponent
            availability_bias = -myd * 5
            contest = (lead * 200) - myd * 5
            target_val = contest + availability_bias
            # Keep track of the best target for this move
            if target_val > my_to:
                my_to = target_val
            if myd < my_to:
                pass
        # Use a second-stage penalty favoring moves that increase separation from opponent (prevents being out-raced).
        sep_before = dist((sx, sy), (ox, oy))
        sep_after = dist((nx, ny), (ox, oy))
        sep_gain = sep_after - sep_before
        val = my_to + sep_gain * 3
        if val > best_val:
            best_val = val
            best_move = [dx, dy]

    return best_move