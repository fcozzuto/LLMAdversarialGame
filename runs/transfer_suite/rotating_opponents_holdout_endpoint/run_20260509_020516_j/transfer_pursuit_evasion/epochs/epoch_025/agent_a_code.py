def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0]) or [0, 0]
    ox, oy = observation.get("opponent_position", [0, 0]) or [0, 0]
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    def pos_list(key):
        out = []
        for it in observation.get(key, []) or []:
            if it is None:
                continue
            if isinstance(it, dict):
                x = it.get("x", it.get(0, None))
                y = it.get("y", it.get(1, None))
            else:
                x, y = it[0], it[1]
            if x is None or y is None:
                continue
            x, y = int(x), int(y)
            if 0 <= x < w and 0 <= y < h:
                out.append((x, y))
        return out

    obstacles = set(pos_list("obstacles"))
    resources = pos_list("resources")
    role = (observation.get("self_role", "") or "").lower()

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def valid(nx, ny):
        return 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles

    def nearest_dist(txs, nx, ny):
        if not txs:
            return 10**9
        best = 10**9
        for tx, ty in txs:
            d = abs(nx - tx) + abs(ny - ty)
            if d < best:
                best = d
        return best

    best = None
    best_score = None
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        d_opp = abs(nx - ox) + abs(ny - oy)
        d_res = nearest_dist(resources, nx, ny)
        # Deterministic scoring:
        # Attacker: closer to resources, farther from opponent
        # Evader: farther from opponent, optionally closer to resources
        if role == "evader":
            score = d_opp * 3 - d_res
        else:
            score = d_res * 3 + d_opp
        if best_score is None or score > best_score:
            best_score = score
            best = [dx, dy]
    if best is not None:
        return best
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if valid(nx, ny):
            return [dx, dy]
    return [0, 0]