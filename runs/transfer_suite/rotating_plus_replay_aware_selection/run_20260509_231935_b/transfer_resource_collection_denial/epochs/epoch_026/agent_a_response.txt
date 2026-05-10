def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [w - 1, h - 1])
    resources = observation.get("resources", []) or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))

    def dist8(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    dirs = [(0, 0), (1, 0), (-1, 0), (0, 1), (0, -1), (1, 1), (1, -1), (-1, 1), (-1, -1)]
    if not resources:
        tx, ty = w - 1, h - 1
        if sx < w // 2 and sx + 1 < w: tx = w - 1
        dx = 0 if tx == sx else (1 if tx > sx else -1)
        dy = 0 if ty == sy else (1 if ty > sy else -1)
        return [dx, dy]

    # Current target bias: focus on resources we are already closest to.
    scored = []
    for rx, ry in resources:
        dself = dist8(sx, sy, rx, ry)
        dopp = dist8(ox, oy, rx, ry)
        scored.append((rx, ry, dself, dopp))
    best_target = min(scored, key=lambda t: (t[2] - t[3], t[2], t[0], t[1]))[:2]
    tx, ty = best_target

    # Evaluate moves by improving "advantage" over opponent.
    best_val = -10**18
    best_moves = []
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if nx < 0 or nx >= w or ny < 0 or ny >= h:
            continue
        if (nx, ny) in obstacles:
            continue

        adv_count = 0
        adv_sum = 0
        closest_dist = 10**9
        closest_opp = 10**9
        for rx, ry, dself, dopp in scored:
            ndself = dist8(nx, ny, rx, ry)
            ndopp = dopp
            if ndself < ndopp:
                adv_count += 1
                adv_sum += (ndopp - ndself)
            cd = ndself
            if cd < closest_dist:
                closest_dist = cd
                closest_opp = ndopp

        # If no immediate advantage change, still progress toward chosen target and avoid giving up.
        target_prog = -dist8(nx, ny, tx, ty)
        stay_penalty = -1 if (dx == 0 and dy == 0) else 0
        give_up_penalty = -(closest_dist - closest_opp) if closest_dist < closest_opp else 0

        val = (adv_count * 1000) + adv_sum * 10 + target_prog * 2 + stay_penalty + give_up_penalty
        if val > best_val:
            best_val = val
            best_moves = [[dx, dy]]
        elif val == best_val:
            best_moves.append([dx, dy])

    # Deterministic tie-break: prefer moves that reduce distance to target, then lexicographic.
    best_moves.sort(key=lambda m: (dist8(sx + m[0], sy + m[1], tx, ty), m[0], m[1]))
    return best_moves[0]