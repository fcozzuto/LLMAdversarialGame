def choose_move(observation):
    w = int(observation["grid_width"])
    h = int(observation["grid_height"])
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            obstacles.add((x, y))

    resources = []
    for r in observation.get("resources") or []:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))
    if not resources:
        return [0, 0]

    def man(a, b, c, d):
        return abs(a - c) + abs(b - d)

    # One-step lookahead: choose move maximizing our advantage over opponent
    best_move = (0, 0)
    best_val = -10**18

    legal = []
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles:
                legal.append((dx, dy, nx, ny))
    if not legal:
        return [0, 0]

    # Deterministic tie-breaking: iterate in fixed order
    legal.sort(key=lambda t: (t[0], t[1], t[2], t[3]))

    for dx, dy, nx, ny in legal:
        # Advantage against the most "contestable" resource
        # Also add a small incentive to get closer to that resource.
        max_adv = -10**18
        chosen_dist = 10**9
        for rx, ry in resources:
            sd = man(nx, ny, rx, ry)
            od = man(ox, oy, rx, ry)
            adv = od - sd
            if adv > max_adv or (adv == max_adv and sd < chosen_dist):
                max_adv = adv
                chosen_dist = sd

        # If we can reach a resource immediately, heavily prefer it
        immediate = 1 if chosen_dist == 0 else 0
        # Penalize moving away from all resources slightly (robustness against denial)
        avg_sd = 0
        for rx, ry in resources:
            avg_sd += man(nx, ny, rx, ry)
        avg_sd //= len(resources)

        val = immediate * 10**6 + max_adv * 1000 - avg_sd
        if val > best_val:
            best_val = val
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]