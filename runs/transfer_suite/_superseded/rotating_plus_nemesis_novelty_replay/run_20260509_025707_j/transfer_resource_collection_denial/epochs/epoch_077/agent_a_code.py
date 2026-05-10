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

    scores = observation.get("scores", {}) or {}
    self_name = observation.get("self_name", "agent_a")
    opp_name = observation.get("opponent_name", "agent_b")
    self_score = scores.get(self_name, 0.0)
    opp_score = scores.get(opp_name, 0.0)
    behind = self_score < opp_score

    tr = observation.get("turns_remaining", 0)
    rem_rc = observation.get("remaining_resource_count", len(resources))

    dirs = [(-1, -1), (0, -1), (1, -1),
            (-1, 0), (0, 0), (1, 0),
            (-1, 1), (0, 1), (1, 1)]

    def ok(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def dist(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    if not resources:
        return [0, 0]

    best = (None, -10**18)
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not ok(nx, ny):
            continue

        move_val = -10**18
        for rx, ry in resources:
            my_d = dist(nx, ny, rx, ry)
            opp_d = dist(ox, oy, rx, ry)
            gap = opp_d - my_d  # positive means we are closer
            # Encourage picking resources we can beat soon; deny resources opponent is nearer to when behind.
            if behind:
                deny_target = (opp_d <= my_d)
                v = (gap * 14 if not deny_target else gap * 6) - my_d * (2 + (tr > 0)) + (deny_target * 8)
            else:
                v = gap * 16 - my_d * (2 + (tr > 0)) + (gap > 0) * (6 + (rem_rc < 6) * 4)
            # Slight preference to head toward opponent when it helps contesting.
            opp_chase = -dist(nx, ny, ox, oy) * 0.05
            v += opp_chase
            if v > move_val:
                move_val = v

        if move_val > best[1]:
            best = ([dx, dy], move_val)

    return best[0] if best[0] is not None else [0, 0]