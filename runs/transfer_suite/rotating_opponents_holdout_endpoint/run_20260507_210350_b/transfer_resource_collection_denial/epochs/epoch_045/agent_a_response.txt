def choose_move(observation):
    w = observation.get("grid_width", 8) or 8
    h = observation.get("grid_height", 8) or 8
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    resources = observation.get("resources", []) or []
    if not resources:
        return [0, 0]
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def inside(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    # Compute a deterministic best-move score: maximize our "lead" on the best resource.
    # lead = (opponent_dist - our_dist); higher is better. Tie-break with safety/commitment.
    best = (float("-inf"), float("inf"), 0, 0)
    best_move = (0, 0)

    # Deterministic ordering of resources for tie-breaking
    res_sorted = sorted(resources, key=lambda r: (int(r[1]), int(r[0])))

    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not inside(nx, ny):
            continue

        # Safety: prefer squares farther from obstacles (Manhattan).
        # If obstacles list is empty, safety stays neutral.
        if obstacles:
            safety = min(abs(nx - ex) + abs(ny - ey) for ex, ey in obstacles)
        else:
            safety = 4

        local_best = float("-inf")
        local_self_dist = float("inf")
        local_target_x = 0
        local_target_y = 0

        for r in res_sorted:
            rx, ry = int(r[0]), int(r[1])
            our_d = abs(rx - nx) + abs(ry - ny)
            opp_d = abs(rx - ox) + abs(ry - oy)
            lead = opp_d - our_d
            # Prefer larger lead; then closer to that resource; then lexicographic target.
            if lead > local_best or (lead == local_best and (our_d < local_self_dist or (our_d == local_self_dist and (rx, ry) < (local_target_x, local_target_y)))):
                local_best = lead
                local_self_dist = our_d
                local_target_x, local_target_y = rx, ry

        # Commitment tie-break: prefer moves that also reduce our distance to the selected target.
        # Use negative local_self_dist to favor smaller distance.
        key = (local_best, -local_self_dist, safety, -local_target_x)
        if key > best:
            best = key
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]