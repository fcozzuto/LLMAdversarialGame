def choose_move(observation):
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    resources = observation.get("resources", []) or []
    obstacles_list = observation.get("obstacles", []) or []
    if not resources:
        return [0, 0]
    obstacles = set((p[0], p[1]) for p in obstacles_list)
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)

    def manh(ax, ay, bx, by):
        d = ax - bx
        if d < 0:
            d = -d
        e = ay - by
        if e < 0:
            e = -e
        return d + e

    moves = [(-1, 0), (1, 0), (0, -1), (0, 1), (-1, -1), (-1, 1), (1, -1), (1, 1), (0, 0)]

    best_move = (0, 0)
    best_score = None

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if nx < 0 or nx >= w or ny < 0 or ny >= h:
            continue
        if (nx, ny) in obstacles and (dx != 0 or dy != 0):
            continue

        worst_blocked = False
        # Score: how much closer we are than opponent to the "most winnable" resource.
        best_adv = None
        best_self_d = None
        best_opp_d = None
        for r in resources:
            rx, ry = r[0], r[1]
            if (rx, ry) in obstacles:
                continue
            sd = manh(nx, ny, rx, ry)
            od = manh(ox, oy, rx, ry)
            adv = od - sd
            if best_adv is None or adv > best_adv or (adv == best_adv and sd < best_self_d):
                best_adv = adv
                best_self_d = sd
                best_opp_d = od

        if best_adv is None:
            continue

        # Prefer higher advantage; break ties by being closer to that resource.
        score = (best_adv, -best_self_d, -best_opp_d, -abs(dx) - abs(dy), dx, dy)
        if best_score is None or score > best_score:
            best_score = score
            best_move = (dx, dy)

    dx, dy = best_move
    if dx not in (-1, 0, 1) or dy not in (-1, 0, 1):
        return [0, 0]
    return [dx, dy]