def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", [])
    obstacles = set(tuple(p) for p in observation.get("obstacles", []))

    deltas = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def dist(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    def in_bounds(x, y):
        return 0 <= x < w and 0 <= y < h

    best_val = -10**9
    best_moves = []

    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not in_bounds(nx, ny):
            continue
        if (nx, ny) in obstacles:
            continue
        if (nx, ny) == (ox, oy):
            pass

        # Choose the resource that gives the biggest immediate advantage after this move.
        # Advantage = (opponent distance - my distance). Higher is better.
        chosen_resource = None
        chosen_adv = -10**9
        chosen_self_d = 10**9
        for rx, ry in resources:
            my_d = dist((nx, ny), (rx, ry))
            opp_d = dist((ox, oy), (rx, ry))
            adv = opp_d - my_d
            if adv > chosen_adv or (adv == chosen_adv and my_d < chosen_self_d):
                chosen_adv = adv
                chosen_self_d = my_d
                chosen_resource = (rx, ry)

        if chosen_resource is None:
            chosen_resource = (ox, oy)
            chosen_adv = -10**9
            chosen_self_d = dist((nx, ny), (ox, oy))

        my_d_to_chosen = dist((nx, ny), chosen_resource)
        opp_d_after = dist((ox, oy), (nx, ny))

        # Primary: maximize advantage to chosen resource.
        # Secondary: minimize distance to chosen resource.
        # Tertiary: maximize separation from opponent.
        val = (chosen_adv * 1000) - my_d_to_chosen + (opp_d_after * 0.001)

        if val > best_val:
            best_val = val
            best_moves = [(dx, dy)]
        elif val == best_val:
            best_moves.append((dx, dy))

    if best_moves:
        # Deterministic tie-break: smallest (dx, dy) in lexicographic order.
        best_moves.sort()
        return [best_moves[0][0], best_moves[0][1]]

    # Fallback: stay still (engine will keep position if invalid move).
    return [0, 0]