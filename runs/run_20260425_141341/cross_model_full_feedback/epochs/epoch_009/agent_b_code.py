def choose_move(observation):
    # Simple deterministic strategy:
    # 1) Move toward the nearest resource by Chebyshev distance, avoiding obstacles.
    # 2) If no reachable resources, move toward the opponent deterministically.
    w = observation["grid_width"]
    h = observation["grid_height"]
    my = observation["self_position"]
    opp = observation["opponent_position"]
    resources = observation.get("resources", [])
    obstacles = set(tuple(p) for p in observation.get("obstacles", []))

    def dist_chebyshev(a, b):
        return max(abs(a[0] - b[0]), abs(a[1] - b[1]))

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

    dx, dy = 0, 0
    if best_res is not None:
        if best_res[0] > my[0]:
            dx = 1
        elif best_res[0] < my[0]:
            dx = -1
        if best_res[1] > my[1]:
            dy = 1
        elif best_res[1] < my[1]:
            dy = -1
    else:
        if opp[0] > my[0]:
            dx = 1
        elif opp[0] < my[0]:
            dx = -1
        if opp[1] > my[1]:
            dy = 1
        elif opp[1] < my[1]:
            dy = -1

    new_x = my[0] + dx
    new_y = my[1] + dy
    if not (0 <= new_x < w and 0 <= new_y < h):
        return [0, 0]
    if (new_x, new_y) in obstacles:
        return [0, 0]

    return [dx, dy]