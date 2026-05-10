def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    obstacles = observation.get("obstacles") or []
    obs = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obs.add((p[0], p[1]))

    deltas = [(-1, -1), (-1, 0), (-1, 1),
              (0, -1), (0, 0), (0, 1),
              (1, -1), (1, 0), (1, 1)]

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obs

    my_moves = []
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if valid(nx, ny):
            my_moves.append((dx, dy, nx, ny))

    def opp_greedy_move(px, py, target_x, target_y):
        best = None
        best_d = 10**9
        for odx, ody in deltas:
            qx, qy = px + odx, py + ody
            if not valid(qx, qy):
                continue
            d = abs(qx - target_x) + abs(qy - target_y)
            # deterministic tie-break: smallest (d, odx, ody)
            key = (d, odx, ody)
            if best is None or key < best:
                best = key
                best = key
                best_move = [odx, ody]
        if best is None:
            return [0, 0]
        return best_move

    def escape_count(x, y):
        c = 0
        for dx, dy in deltas:
            nx, ny = x + dx, y + dy
            if valid(nx, ny):
                c += 1
        return c

    best_move = [0, 0]
    best_score = None
    for dx, dy, nx, ny in my_moves:
        # opponent chases us greedily toward our new position
        odx, ody = opp_greedy_move(ox, oy, nx, ny)
        n_ox, n_oy = ox + odx, oy + ody

        # if capture occurs (radius 0)
        if n_ox == nx and n_oy == ny:
            cap_penalty = -10**6
            # still compute tie-breaks deterministically
            score = (cap_penalty, -escape_count(nx, ny), 0)
        else:
            dist = abs(nx - n_ox) + abs(ny - n_oy)
            # prefer larger distance, then more escape options, then deterministic preference
            score = (dist, escape_count(nx, ny), -(abs(dx) + abs(dy)))

        if best_score is None or score > best_score:
            best_score = score
            best_move = [dx, dy]

    return best_move