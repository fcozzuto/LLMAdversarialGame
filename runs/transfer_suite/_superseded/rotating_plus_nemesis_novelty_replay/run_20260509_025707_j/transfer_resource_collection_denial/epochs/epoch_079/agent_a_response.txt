def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    resources = observation.get("resources", []) or []
    obstacles = set()
    for p in observation.get("obstacles", []) or []:
        if p and len(p) >= 2:
            obstacles.add((p[0], p[1]))
    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    tr = observation.get("turns_remaining", 0)

    def ok(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    if not resources:
        return [0, 0]

    def man(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    scored = []
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not ok(nx, ny):
            continue

        best_gap = -10**9
        best_my_d = 10**9
        pos_gap_sum = 0
        closest_opp_d = 10**9

        for r in resources:
            rx, ry = r[0], r[1]
            my_d = man(nx, ny, rx, ry)
            opp_d = man(ox, oy, rx, ry)
            gap = opp_d - my_d
            if gap > best_gap or (gap == best_gap and my_d < best_my_d):
                best_gap = gap
                best_my_d = my_d
            if gap > 0:
                pos_gap_sum += gap
            if opp_d < closest_opp_d:
                closest_opp_d = opp_d

        # Prefer turning into a lead (resource_denier hates losing targets), then faster capture,
        # then reduce opponent's best access.
        # Early game: stronger lead; late game: urgency.
        lead_weight = 3 if tr > 16 else 2
        urgency_weight = 2 if tr <= 16 else 1
        value = (lead_weight * best_gap + pos_gap_sum, -urgency_weight * best_my_d - closest_opp_d)
        scored.append((value, [dx, dy]))

    scored.sort(key=lambda x: (x[0][0], x[0][1]), reverse=True)
    return scored[0][1] if scored else [0, 0]