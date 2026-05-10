def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w, h = observation["grid_width"], observation["grid_height"]
    obstacles = set(tuple(p) for p in observation.get("obstacles") or [])
    resources = observation.get("resources") or []
    if not resources:
        return [0, 0]

    def dist(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    best = None
    best_key = None
    for rx, ry in resources:
        sd = abs(rx - sx) + abs(ry - sy)
        od = abs(rx - ox) + abs(ry - oy)
        key = (od - sd, -sd)  # prioritize resources where we arrive earlier; then closer
        if best is None or key > best_key:
            best, best_key = (rx, ry), key

    tx, ty = best
    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    scored = []
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if nx < 0 or nx >= w or ny < 0 or ny >= h:
            continue
        if (nx, ny) in obstacles:
            continue
        d_to = abs(tx - nx) + abs(ty - ny)
        d_opp = abs(tx - ox) + abs(ty - oy)
        step_adv = (d_opp - d_to)
        # Also discourage moving away from our target and moving into opponent vicinity
        opp_near = - (abs(nx - ox) + abs(ny - oy))
        score = (step_adv, -d_to, opp_near, -abs(dx) - abs(dy))
        scored.append((score, dx, dy))
    if not scored:
        return [0, 0]
    scored.sort(reverse=True)
    return [scored[0][1], scored[0][2]]