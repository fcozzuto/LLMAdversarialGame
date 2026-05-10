def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w, h = observation["grid_width"], observation["grid_height"]
    resources = observation.get("resources") or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles") or []))

    if not resources:
        tx, ty = w // 2, h // 2
        dx = 0 if tx == sx else (1 if tx > sx else -1)
        dy = 0 if ty == sy else (1 if ty > sy else -1)
        return [dx, dy]

    res = [tuple(p) for p in resources]
    deltas = [(0, 0), (1, 0), (0, 1), (-1, 0), (0, -1), (1, 1), (-1, 1), (1, -1), (-1, -1)]

    def man(ax, ay, bx, by):
        return abs(ax - bx) + abs(ay - by)

    best = [0, 0]
    best_val = -10**18

    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if nx < 0 or nx >= w or ny < 0 or ny >= h:
            continue
        if (nx, ny) in obstacles:
            continue

        pickup = 1000 if (nx, ny) in obstacles else 0  # no-op, keeps deterministic structure
        if (nx, ny) in res:
            pickup = 200000  # decisive when we can collect now

        my_best = 10**9
        opp_best = 10**9
        best_adv = -10**9
        for rx, ry in res:
            md = man(nx, ny, rx, ry)
            od = man(ox, oy, rx, ry)
            if md < my_best:
                my_best = md
            if od < opp_best:
                opp_best = od
            adv = od - md  # positive means we are closer to that resource than opponent
            if adv > best_adv:
                best_adv = adv

        # Prefer immediate pickups, then maximizing being closer than opponent,
        # and finally moving to reduce our distance.
        val = pickup
        val += 5000 * best_adv
        val += -3 * my_best
        val += -0.5 * abs((w + h) - (my_best + opp_best)) * 0  # deterministic neutral term

        if val > best_val:
            best_val = val
            best = [dx, dy]

    return best