def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    resources = observation.get("resources", []) or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))
    if not resources:
        best = [0, 0]
        bestv = -10**9
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                nx, ny = sx + dx, sy + dy
                if nx < 0 or nx >= w or ny < 0 or ny >= h or (nx, ny) in obstacles:
                    continue
                dv = max(abs(nx - ox), abs(ny - oy))
                if dv > bestv:
                    bestv = dv
                    best = [dx, dy]
        return best

    def dist(a, b):
        return max(abs(a[0] - b[0]), abs(a[1] - b[1]))

    best_res = None
    best_key = None
    for r in resources:
        rx, ry = r
        if (rx, ry) in obstacles:
            continue
        dS = dist((sx, sy), (rx, ry))
        dO = dist((ox, oy), (rx, ry))
        key = (dS - dO, dS, abs(rx - sx) + abs(ry - sy))
        if best_key is None or key < best_key:
            best_key = key
            best_res = (rx, ry)

    tx, ty = best_res
    # If opponent is much closer to our chosen target, bias toward creating separation
    opp_bias = 1 if best_key and best_key[0] > 0 else 0
    best_move = [0, 0]
    best_score = None
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            if nx < 0 or nx >= w or ny < 0 or ny >= h or (nx, ny) in obstacles:
                continue
            dT = dist((nx, ny), (tx, ty))
            dO = dist((nx, ny), (ox, oy))
            # primary: reduce distance to target; secondary: avoid opponent
            score = (dT, -(dO if opp_bias else 0), abs(nx - tx) + abs(ny - ty), abs(dx) + abs(dy))
            if best_score is None or score < best_score:
                best_score = score
                best_move = [dx, dy]
    return best_move