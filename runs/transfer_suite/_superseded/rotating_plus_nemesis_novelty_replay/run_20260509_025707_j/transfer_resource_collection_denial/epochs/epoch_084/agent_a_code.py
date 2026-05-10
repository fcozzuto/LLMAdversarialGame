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
    tr = observation.get("turns_remaining", 0)

    dirs = [(-1, -1), (0, -1), (1, -1),
            (-1, 0), (0, 0), (1, 0),
            (-1, 1), (0, 1), (1, 1)]

    def ok(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def dist(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    if not resources:
        return [0, 0]

    # Prefer collecting earliest when it makes us strictly ahead; otherwise try to avoid being beaten on near targets.
    best = [0, 0]
    best_val = -10**18
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not ok(nx, ny):
            continue

        my_future = []
        for r in resources:
            rx, ry = r[0], r[1]
            my_d = dist(nx, ny, rx, ry)
            opp_d = dist(ox, oy, rx, ry)
            my_future.append((my_d, opp_d, rx, ry))
        my_future.sort(key=lambda t: t[0])

        val = -my_future[0][0] if my_future else 0
        # Evaluate only the most promising few deterministically
        for i, (my_d, opp_d, rx, ry) in enumerate(my_future[:6]):
            ahead = 1 if my_d < opp_d else 0
            tie = 1 if my_d == opp_d else 0
            gap = opp_d - my_d
            # Big incentive to be ahead on close resources
            part = 0
            if my_d <= 2:
                part += 120
            if ahead:
                part += 70 + 12 * min(5, gap)
            if tie:
                part += 25
            # Strongly discourage walking into a resource where opponent is very close
            if opp_d <= 2 and my_d > opp_d:
                part -= 90 + 15 * min(5, opp_d)
            # Slight preference to reduce opponent's lead when both are far
            part += 6 * min(10, gap)
            # If time is running out, push for nearest available
            if tr <= 8:
                part += 10 * max(0, 3 - my_d)
            # Prefer moves that also "point" toward multiple targets
            if i == 0:
                part += 30
            val += part

        if val > best_val:
            best_val = val
            best = [dx, dy]
    return best