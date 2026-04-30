def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources") or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles") or []))

    def cheb(a, b):
        return abs(a[0] - b[0]) if abs(a[0] - b[0]) > abs(a[1] - b[1]) else abs(a[1] - b[1])

    dirs = [(0, 0), (1, 0), (-1, 0), (0, 1), (0, -1), (1, 1), (1, -1), (-1, 1), (-1, -1)]
    best_move = [0, 0]
    best_key = None

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if nx < 0 or nx >= w or ny < 0 or ny >= h:
            continue
        if (nx, ny) in obstacles:
            continue

        my_pos = (nx, ny)
        my_to_opp = cheb(my_pos, (ox, oy))

        if resources:
            best_res_key = None
            for rx, ry in resources:
                if (rx, ry) in obstacles:
                    continue
                md = cheb(my_pos, (rx, ry))
                od = cheb((ox, oy), (rx, ry))
                # Prefer resources I can reach at least as fast; then maximize advantage; then closer.
                key = (0 if md <= od else 1, md - od, -md, rx, ry)
                if best_res_key is None or key < best_res_key:
                    best_res_key = key
            if best_res_key is None:
                res_score = (1, 0)
            else:
                res_score = (best_res_key[0], best_res_key[1])
            key = (res_score[0], res_score[1], my_to_opp, -nx, -ny)
        else:
            # No resources: try to reduce distance to opponent deterministically.
            key = (1, my_to_opp, nx, ny)

        if best_key is None or key < best_key:
            best_key = key
            best_move = [dx, dy]

    return best_move