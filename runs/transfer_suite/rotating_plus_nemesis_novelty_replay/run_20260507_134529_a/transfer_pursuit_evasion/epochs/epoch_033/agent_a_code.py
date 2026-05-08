def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", (0, 0)) or (0, 0)
    ox, oy = observation.get("opponent_position", (0, 0)) or (0, 0)
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if p is not None and len(p) >= 2:
            obstacles.add((int(p[0]), int(p[1])))

    self_role = (observation.get("self_role") or "").lower()
    opponent_role = (observation.get("opponent_role") or "").lower()
    is_evader = ("evader" in self_role) or ("evader" in opponent_role and "pursuer" not in self_role)
    is_evader = bool(is_evader) and ("pursuer" not in self_role or "evader" in self_role)

    moves = [(-1,-1),(-1,0),(-1,1),(0,-1),(0,0),(0,1),(1,-1),(1,0),(1,1)]
    def ok(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def dist2(x, y):
        dx, dy = x - ox, y - oy
        return dx*dx + dy*dy

    parity = int(observation.get("turn_index", 0) or 0) & 1
    best_move = [0, 0]
    if is_evader:
        bestv = -10**18
    else:
        bestv = 10**18

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not ok(nx, ny):
            continue

        d = dist2(nx, ny)
        if not is_evader and nx == ox and ny == oy:
            return [dx, dy]

        # small innovation for zigzag: alternate preference to "cut" across opponent drift
        drift_x = (1 if ox > sx else -1 if ox < sx else 0)
        drift_y = (1 if oy > sy else -1 if oy < sy else 0)
        dot = drift_x * dx + drift_y * dy  # -2..2

        # obstacle pressure: avoid tight/blocked cells
        neigh_obs = 0
        for ax in (-1, 0, 1):
            for ay in (-1, 0, 1):
                if ax == 0 and ay == 0:
                    continue
                tx, ty = nx + ax, ny + ay
                if not (0 <= tx < w and 0 <= ty < h) or (tx, ty) in obstacles:
                    neigh_obs += 1

        score = d
        if is_evader:
            score = score * 4 - neigh_obs
            if parity == 0:
                score += dot
            else:
                score -= dot
        else:
            score = score * 4 + neigh_obs
            if parity == 0:
                score -= dot
            else:
                score += dot

        if is_evader:
            if score > bestv:
                bestv, best_move = score, [dx, dy]
        else:
            if score < bestv:
                bestv, best_move = score, [dx, dy]

    return best_move