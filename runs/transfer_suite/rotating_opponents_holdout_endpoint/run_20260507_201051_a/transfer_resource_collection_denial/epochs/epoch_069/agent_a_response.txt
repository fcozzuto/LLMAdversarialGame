def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sx, sy = observation.get("self_position") or (0, 0)
    ox, oy = observation.get("opponent_position") or (w - 1, h - 1)
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for p in observation.get("resources") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    def clamp_move(dx, dy):
        nx, ny = sx + dx, sy + dy
        if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles:
            return nx, ny
        return sx, sy

    def dist(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    if not resources:
        best = [0, 0]
        best_sc = -10**9
        for dx, dy in dirs:
            nx, ny = clamp_move(dx, dy)
            d_away = dist((nx, ny), (ox, oy))
            if d_away > best_sc:
                best_sc = d_away
                best = [dx if nx != sx else 0, dy if ny != sy else 0]
        return best

    opp_resources_sorted = sorted(resources, key=lambda r: dist((ox, oy), r))
    nearest_opp = opp_resources_sorted[0]
    opp_d_near = dist((ox, oy), nearest_opp)

    best = [0, 0]
    best_sc = -10**18
    for dx, dy in dirs:
        nx, ny = clamp_move(dx, dy)
        my_pos = (nx, ny)

        # Prefer resources where we can beat the opponent; deprioritize what opponent is already closest to.
        local_sc = 0
        for r in resources:
            my_d = dist(my_pos, r)
            opp_d = dist((ox, oy), r)
            adv = (opp_d - my_d)  # positive means we are closer
            # heavy bias toward securing a resource now; slight penalty if opponent is extremely close to it
            urgency = 2 if my_d <= 2 else 1
            opp_pressure = 3 if opp_d <= 2 else 1
            penalty_toward_opp = 2 if r == nearest_opp else 0
            local_sc = max(local_sc, urgency * adv - opp_pressure * (1 if adv < 0 else 0) - penalty_toward_opp)

        # Secondary objective: keep distance while moving, to avoid being "dragged" by opponent toward same targets.
        local_sc += 0.15 * dist(my_pos, (ox, oy))

        # If we fail to beat the opponent's nearest, add a small penalty to encourage alternative targets.
        if dist(my_pos, nearest_opp) >= opp_d_near:
            local_sc -= 1.25

        if local_sc > best_sc:
            best_sc = local_sc
            best = [dx if (sx + dx, sy + dy) != (sx, sy) else 0, dy if (sx + dx, sy + dy) != (sx, sy) else 0]

    return best