def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w, h = observation["grid_width"], observation["grid_height"]
    resources = observation.get("resources") or []
    obstacles_list = observation.get("obstacles") or []
    obstacles = set()
    for p in obstacles_list:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obstacles.add((p[0], p[1]))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0:
            dx = -dx
        dy = ay - by
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    if not resources:
        return [0, 0]

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best_move = (0, 0)
    best_score = -10**18

    # Target evaluation: prioritize resources where we are relatively closer than opponent.
    # For each move, approximate by the best resource we could secure soonest.
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue

        if (nx, ny) in resources:
            return [dx, dy]

        local_best = (-10**18, 10**18, 10**18, 0, 0)  # (lead, self_dist, opp_dist, rx, ry)
        for rx, ry in resources:
            if (rx, ry) in obstacles:
                continue
            sd = cheb(nx, ny, rx, ry)
            od = cheb(ox, oy, rx, ry)
            lead = od - sd
            cand = (lead, sd, od, rx, ry)
            if (lead, -sd, -od, -rx, -ry) > (local_best[0], -local_best[1], -local_best[2], -local_best[3], -local_best[4]):
                local_best = cand

        lead, sd, od, rx, ry = local_best
        # If we're not leading, still move to reduce our distance; break ties deterministically.
        score = lead * 1000 - sd * 10 - od
        # Slight preference to stay mobile (avoid getting stuck near obstacles edges).
        edge_pen = 0
        if nx == 0 or nx == w - 1 or ny == 0 or ny == h - 1:
            edge_pen += 1
        score -= edge_pen
        # Deterministic tie-break: prefer lexicographically smaller move delta.
        if score > best_score or (score == best_score and (dx, dy) < best_move):
            best_score = score
            best_move = (dx, dy)

    return [best_move[0], best_move[1]]