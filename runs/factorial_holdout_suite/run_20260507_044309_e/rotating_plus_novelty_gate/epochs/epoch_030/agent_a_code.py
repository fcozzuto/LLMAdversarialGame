def choose_move(observation):
    w = observation["grid_width"]; h = observation["grid_height"]
    sx, sy = observation["self_position"]; ox, oy = observation["opponent_position"]
    obstacles = {(p[0], p[1]) for p in (observation.get("obstacles", []) or [])}
    resources = observation.get("resources", []) or []
    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def dist(a, b):
        return max(abs(a[0] - b[0]), abs(a[1] - b[1]))

    # Immediate pickup if possible
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if inb(nx, ny):
            for rx, ry in resources:
                if nx == rx and ny == ry:
                    return [dx, dy]

    if not resources:
        return [0, 0]

    best_move = (0, 0)
    best_val = -10**9
    best_tdist = 10**9
    best_topp = -10**9

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue

        # Evaluate by best attainable resource advantage from next position
        best_adv = -10**9
        best_resource = None
        best_self_d = 10**9
        best_opp_d = -10**9
        for rx, ry in resources:
            sd = dist((nx, ny), (rx, ry))
            od = dist((ox, oy), (rx, ry))
            adv = od - sd
            if adv > best_adv or (adv == best_adv and (sd < best_self_d or (sd == best_self_d and od > best_opp_d))):
                best_adv = adv
                best_self_d = sd
                best_opp_d = od
                best_resource = (rx, ry)

        # Primary: maximize advantage; secondary: minimize our distance to that target
        # Tertiary: if tied, slightly prefer moves that get closer to opponent to contest effectively
        val = best_adv * 1000 - best_self_d
        if best_resource is not None:
            val += (dist((nx, ny), (ox, oy)) < dist((sx, sy), (ox, oy))) * 5

        if val > best_val or (val == best_val and best_self_d < best_tdist) or (val == best_val and best_self_d == best_tdist and best_opp_d > best_topp):
            best_val = val
            best_move = (dx, dy)
            best_tdist = best_self_d
            best_topp = best_opp_d

    return [best_move[0], best_move[1]]