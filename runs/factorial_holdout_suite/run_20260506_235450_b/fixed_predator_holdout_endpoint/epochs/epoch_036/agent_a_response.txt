def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    resources = observation.get("resources", []) or []
    obstacles_list = observation.get("obstacles", []) or []
    obstacles = set((p[0], p[1]) for p in obstacles_list)

    if not resources:
        return [0, 0]

    res = [(int(r[0]), int(r[1])) for r in resources]
    res_set = set(res)

    def in_bounds(x, y):
        return 0 <= x < w and 0 <= y < h

    dirs = [(-1, -1), (-1, 0), (-1, 1),
            (0, -1), (0, 0), (0, 1),
            (1, -1), (1, 0), (1, 1)]

    # Margin: how much closer we are than opponent to a given resource; higher is better.
    def best_margin(px, py):
        best = None
        best_self_d = None
        for rx, ry in res:
            sd = abs(px - rx) + abs(py - ry)
            od = abs(ox - rx) + abs(oy - ry)
            m = od - sd
            if best is None or m > best or (m == best and sd < best_self_d):
                best = m
                best_self_d = sd
        return best, best_self_d

    cur_margin, cur_sd = best_margin(sx, sy)

    best_move = [0, 0]
    best_val = None

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not in_bounds(nx, ny):
            continue
        if (nx, ny) in obstacles:
            continue

        m, sd = best_margin(nx, ny)
        grab = 1 if (nx, ny) in res_set else 0

        # Encourage immediate grabs, then improve margin over current, then reduce own distance.
        val = (grab, m - cur_margin, -sd)

        if best_val is None or val > best_val:
            best_val = val
            best_move = [dx, dy]

    return best_move