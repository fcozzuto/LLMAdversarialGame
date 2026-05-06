def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    x, y = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", [])
    obstacles = set(tuple(p) for p in observation.get("obstacles", []))

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def inb(nx, ny):
        return 0 <= nx < w and 0 <= ny < h

    def blocked(nx, ny):
        return (nx, ny) in obstacles

    def dist(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    def sign(v):
        return 0 if v == 0 else (1 if v > 0 else -1)

    if not resources:
        return [-sign(ox - x), -sign(oy - y)]

    best = (0, 0)
    best_sc = -10**18
    cur_opp_d = dist((x, y), (ox, oy))

    for dx, dy in dirs:
        nx, ny = x + dx, y + dy
        if not inb(nx, ny) or blocked(nx, ny):
            continue

        self_next = (nx, ny)
        opp_d = dist(self_next, (ox, oy))
        opp_reach_pressure = cur_opp_d - opp_d  # positive if we get closer to opponent

        # Resource advantage: we want to be closer than opponent, especially for near resources.
        # Deterministic tie-break naturally handled by strict comparisons.
        adv_sum = 0
        near_bonus = 0
        for r in resources:
            sd = dist(self_next, r)
            od = dist((ox, oy), r)
            gap = od - sd  # positive => we are closer than opponent
            # emphasize closer resources and bigger gap; also slight preference to reduce our distance
            adv_sum += gap * 3 - sd
            if sd <= 4:
                near_bonus += gap * 2 - sd

        # Encourage taking a resource if it gives us advantage; otherwise maintain pressure on opponent.
        sc = adv_sum + 5 * near_bonus + 2 * opp_reach_pressure
        # small stability penalty to avoid oscillation away from best direction
        sc -= 0 if (dx == 0 and dy == 0) else 0

        if sc > best_sc:
            best_sc = sc
            best = (dx, dy)

    return [best[0], best[1]]