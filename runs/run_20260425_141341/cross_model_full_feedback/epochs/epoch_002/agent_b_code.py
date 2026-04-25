def choose_move(observation):
    # Deterministic strategy for agent_b
    turn = observation.get("turn_index", 0)
    w = observation["grid_width"]
    h = observation["grid_height"]

    my = observation["self_position"]  # [x, y]
    opp = observation["opponent_position"]

    resources = observation.get("resources", [])
    obstacles = set(tuple(p) for p in observation.get("obstacles", []))

    # Helper distances
    def dist_chebyshev(a, b):
        return max(abs(a[0] - b[0]), abs(a[1] - b[1]))

    # If there are resources, target the closest available resource
    best_res = None
    best_dist = None
    for r in resources:
        rxy = tuple(r)
        if rxy in obstacles:
            continue
        d = dist_chebyshev(my, rxy)
        if best_dist is None or d < best_dist:
            best_dist = d
            best_res = rxy

    candidate = [0, 0]

    if best_res is not None:
        dx = 0
        dy = 0
        if best_res[0] > my[0]:
            dx = 1
        elif best_res[0] < my[0]:
            dx = -1
        if best_res[1] > my[1]:
            dy = 1
        elif best_res[1] < my[1]:
            dy = -1
        candidate = [dx, dy]
    else:
        # No resource: move toward opponent
        dx = 0
        dy = 0
        if opp[0] > my[0]:
            dx = 1
        elif opp[0] < my[0]:
            dx = -1
        if opp[1] > my[1]:
            dy = 1
        elif opp[1] < my[1]:
            dy = -1
        candidate = [dx, dy]

    # Clamp to allowed move range (-1, 0, 1)
    for i in range(2):
        if candidate[i] < -1:
            candidate[i] = -1
        if candidate[i] > 1:
            candidate[i] = 1

    # If moving into obstacle or out of bounds, stay in place
    new_x = my[0] + candidate[0]
    new_y = my[1] + candidate[1]
    if not (0 <= new_x < w and 0 <= new_y < h):
        return [0, 0]
    if (new_x, new_y) in obstacles:
        return [0, 0]

    return candidate