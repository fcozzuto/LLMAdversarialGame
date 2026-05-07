def choose_move(observation):
    def to_xy(v):
        if isinstance(v, (list, tuple)) and len(v) >= 2:
            return int(v[0]), int(v[1])
        return 0, 0

    sx, sy = to_xy(observation.get("self_position"))
    ox, oy = to_xy(observation.get("opponent_position"))
    gw = int(observation.get("grid_width", 8) or 8)
    gh = int(observation.get("grid_height", 8) or 8)

    obstacles = set()
    for it in observation.get("obstacles") or []:
        x, y = to_xy(it)
        if 0 <= x < gw and 0 <= y < gh:
            obstacles.add((x, y))

    resources = []
    for it in observation.get("resources") or []:
        x, y = to_xy(it)
        if 0 <= x < gw and 0 <= y < gh and (x, y) not in obstacles:
            resources.append((x, y))
    if not resources:
        return [0, 0]

    def manh(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0:
            dx = -dx
        dy = y1 - y2
        if dy < 0:
            dy = -dy
        return dx + dy

    # Predict opponent immediate target: nearest by Manhattan (tie-break deterministically).
    opp_target = min(resources, key=lambda r: (manh(ox, oy, r[0], r[1]), r[0], r[1]))
    opp_td = manh(ox, oy, opp_target[0], opp_target[1])

    # Score resources by "steal margin": how much sooner we arrive vs opponent.
    # Add a small preference to avoid far detours and to break ties deterministically.
    best_r = None
    best_k = None
    for r in resources:
        sd = manh(sx, sy, r[0], r[1])
        od = manh(ox, oy, r[0], r[1])
        margin = od - sd  # positive => we can arrive earlier
        # If opponent is likely going for opp_target, strongly weight taking it if possible.
        focus = 5 if (r[0], r[1]) == opp_target else 0
        k = (margin + focus, -sd, r[0], r[1])
        if best_k is None or k > best_k:
            best_k, best_r = k, r

    tx, ty = best_r
    dx = 0 if tx == sx else (1 if tx > sx else -1)
    dy = 0 if ty == sy else (1 if ty > sy else -1)
    return [dx, dy]