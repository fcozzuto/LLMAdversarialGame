def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    obstacles = set((p[0], p[1]) for p in observation["obstacles"])
    resources = observation["resources"]

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def clamp_in_bounds(x, y):
        if x < 0: x = 0
        elif x >= w: x = w - 1
        if y < 0: y = 0
        elif y >= h: y = h - 1
        return x, y

    def dist(a, b):
        # Chebyshev distance suits 8-neighbor movement
        return max(abs(a[0] - b[0]), abs(a[1] - b[1]))

    if not resources:
        # No resources visible: move away from opponent slightly to avoid collisions, deterministic.
        best = (10**9, 0, 0)
        for dx, dy in deltas:
            nx, ny = clamp_in_bounds(sx + dx, sy + dy)
            if (nx, ny) in obstacles:
                continue
            d_to_opp = dist((nx, ny), (ox, oy))
            if (d_to_opp, -dx, -dy) > (best[0], best[1], best[2]):
                best = (d_to_opp, -dx, -dy)
        return [-best[1], -best[2]] if best[0] != 10**9 else [0, 0]

    best_move = (None, -10**18)
    resources_sorted = sorted(resources, key=lambda p: (p[0], p[1]))

    for dx, dy in deltas:
        nx, ny = clamp_in_bounds(sx + dx, sy + dy)
        if (nx, ny) in obstacles:
            continue
        my_pos = (nx, ny)
        score = -10**18
        for rx, ry in resources_sorted:
            rpos = (rx, ry)
            my_d = dist(my_pos, rpos)
            opp_d = dist((ox, oy), rpos)
            # Prefer states where we are closer than opponent to a specific resource.
            local = (opp_d - my_d) * 100 - my_d
            # Small tie-break to prefer earlier capture when opponent is far.
            local += (1 if opp_d > my_d else 0) * 5
            if local > score:
                score = local
        # Prefer moves that also slightly increase distance to opponent if tied.
        opp_sep = dist(my_pos, (ox, oy))
        tie = score * 1000 + opp_sep
        if tie > best_move[1]:
            best_move = ((dx, dy), tie)

    if best_move[0] is None:
        return [0, 0]
    return [best_move[0][0], best_move[0][1]]