def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position", [0, 0]) or [0, 0]
    op = observation.get("opponent_position", [0, 0]) or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obs_set = set()
    for p in observation.get("obstacles", []) or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obs_set.add((x, y))

    self_role = (observation.get("self_role", "") or "").lower()
    opponent_role = (observation.get("opponent_role", "") or "").lower()
    self_is_evader = ("evad" in self_role) or (self_role == "evader") or ("evad" in opponent_role)

    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def ok(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obs_set

    def d2(x1, y1, x2, y2):
        dx, dy = x1 - x2, y1 - y2
        return dx * dx + dy * dy

    best_move = [0, 0]
    best_score = None

    if self_is_evader:
        corners = [(0, 0), (w - 1, 0), (0, h - 1), (w - 1, h - 1)]
        tx, ty = corners[0]
        best_corner = -1
        for cx, cy in corners:
            if (cx, cy) in obs_set:
                continue
            s = d2(cx, cy, ox, oy)
            if s > best_corner:
                best_corner = s
                tx, ty = cx, cy
    else:
        tx, ty = ox, oy

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not ok(nx, ny):
            continue
        dist_to_opp = d2(nx, ny, ox, oy)
        dist_to_target = d2(nx, ny, tx, ty)
        # penalize proximity to obstacles
        near_obs = 0
        for adx in (-1, 0, 1):
            for ady in (-1, 0, 1):
                if adx == 0 and ady == 0:
                    continue
                ax, ay = nx + adx, ny + ady
                if 0 <= ax < w and 0 <= ay < h and (ax, ay) in obs_set:
                    near_obs += 1
        if self_is_evader:
            score = (-dist_to_opp, dist_to_target, near_obs, nx, ny)
        else:
            score = (dist_to_opp, dist_to_target, near_obs, -nx, -ny)

        if best_score is None or score < best_score:
            best_score = score
            best_move = [dx, dy]

    return best_move if ok(sx + best_move[0], sy + best_move[1]) else [0, 0]