def choose_move(observation):
    w = observation["grid_width"]; h = observation["grid_height"]
    sx, sy = observation["self_position"]; ox, oy = observation["opponent_position"]
    resources = observation["resources"]; obstacles = set(tuple(p) for p in observation["obstacles"])
    def inb(x, y): return 0 <= x < w and 0 <= y < h
    def dist(a, b): return max(abs(a[0]-b[0]), abs(a[1]-b[1]))  # Chebyshev for 8-dir
    self_pos = (sx, sy); opp_pos = (ox, oy)

    best_target = None; best_val = -10**9
    for rx, ry in resources:
        if (rx, ry) in obstacles: 
            continue
        sd = dist(self_pos, (rx, ry))
        od = dist(opp_pos, (rx, ry))
        val = (od - sd) * 3 - sd  # prefer being closer than opponent
        if val > best_val:
            best_val = val; best_target = (rx, ry)
    if best_target is None:
        # fallback: move toward center
        cx, cy = w // 2, h // 2
        tx, ty = cx, cy
    else:
        tx, ty = best_target

    moves = [(dx, dy) for dx in (-1, 0, 1) for dy in (-1, 0, 1)]
    legal = []
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if inb(nx, ny) and (nx, ny) not in obstacles:
            legal.append((dx, dy))
    if not legal:
        return [0, 0]

    # If opponent is very close to the target, bias toward next-best resource deterministically
    opp_to_t = dist(opp_pos, (tx, ty))
    self_to_t = dist(self_pos, (tx, ty))
    if opp_to_t <= self_to_t and len(resources) > 1:
        alt_target = None; alt_val = -10**9
        for rx, ry in resources:
            if (rx, ry) in obstacles: 
                continue
            sd = dist(self_pos, (rx, ry))
            od = dist(opp_pos, (rx, ry))
            val = (od - sd) * 4 - sd
            if (rx, ry) != (tx, ty) and val > alt_val:
                alt_val = val; alt_target = (rx, ry)
        if alt_target is not None:
            tx, ty = alt_target

    # Pick move that minimizes distance to target; tie-break deterministically
    best_move = (0, 0); best_score = 10**9
    for dx, dy in legal:
        nx, ny = sx + dx, sy + dy
        d = dist((nx, ny), (tx, ty))
        # small tie-breakers to avoid oscillation: prefer reducing x-distance then y-distance
        score = d * 100 + abs(nx - tx) * 2 + abs(ny - ty)
        if score < best_score or (score == best_score and (dx, dy) < best_move):
            best_score = score; best_move = (dx, dy)
    return [int(best_move[0]), int(best_move[1])]