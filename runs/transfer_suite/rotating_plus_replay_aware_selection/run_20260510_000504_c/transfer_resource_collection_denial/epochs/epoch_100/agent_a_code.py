def choose_move(observation):
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)

    resources = observation.get("resources") or []
    obstacles = observation.get("obstacles") or []

    obs = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obs.add((int(p[0]), int(p[1])))
        elif isinstance(p, dict):
            q = p.get("position", None)
            if isinstance(q, (list, tuple)) and len(q) >= 2:
                obs.add((int(q[0]), int(q[1])))
            elif "x" in p and "y" in p:
                obs.add((int(p["x"]), int(p["y"])))

    res = []
    for r in resources:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            res.append((int(r[0]), int(r[1])))
        elif isinstance(r, dict):
            q = r.get("position", None)
            if isinstance(q, (list, tuple)) and len(q) >= 2:
                res.append((int(q[0]), int(q[1])))
            elif "x" in r and "y" in r:
                res.append((int(r["x"]), int(r["y"])))

    if not res:
        return [0, 0]

    def dist(a, b):
        ax, ay = a
        bx, by = b
        dx = ax - bx
        dy = ay - by
        if dx < 0: dx = -dx
        if dy < 0: dy = -dy
        return dx if dx > dy else dy  # Chebyshev (diagonals allowed)

    deltas = [(-1,-1),(-1,0),(-1,1),(0,-1),(0,0),(0,1),(1,-1),(1,0),(1,1)]
    best_move = [0, 0]
    best_score = -10**18

    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if nx < 0 or nx >= w or ny < 0 or ny >= h:
            continue
        if (nx, ny) in obs:
            continue

        # Greedy resource pressure vs opponent
        score = 0
        nearest_self = 10**9
        nearest_opp = 10**9
        for rx, ry in res:
            d_s = dist((nx, ny), (rx, ry))
            d_o = dist((ox, oy), (rx, ry))
            if d_s < nearest_self: nearest_self = d_s
            if d_o < nearest_opp: nearest_opp = d_o
            # prefer resources where we are not behind opponent
            adv = d_o - d_s
            if adv > 0:
                score += 40 * adv - d_s
            else:
                score += -10 * (-adv) - 0.5 * d_s

        # center bias when tied
        cx, cy = (w - 1) / 2.0, (h - 1) / 2.0
        score -= 0.01 * (abs(nx - cx) + abs(ny - cy))

        # small preference to reduce distance to opponent when far (denier)
        score += 0.02 * dist((nx, ny), (ox, oy))

        # deterministic tie-breaker: lexicographic on move via score then dx,dy
        if score > best_score or (score == best_score and (dx, dy) < (best_move[0], best_move[1])):
            best_score = score
            best_move = [dx, dy]

    # If all moves blocked, stay
    return [int(best_move[0]), int(best_move[1])]