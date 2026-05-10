def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sx, sy = observation.get("self_position") or [0, 0]
    ox, oy = observation.get("opponent_position") or [0, 0]
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obs = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obs.add((x, y))

    resources = []
    for p in observation.get("resources") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                resources.append((x, y))

    sr = str(observation.get("self_role", "")).lower()
    evader = ("evad" in sr) or ("escape" in sr) or ("runner" in sr) or ("evasion" in sr)

    deltas = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def man2(x1, y1, x2, y2):
        dx, dy = x1 - x2, y1 - y2
        return dx * dx + dy * dy

    def nearest_res_dist2(nx, ny):
        if not resources:
            return 0
        best = 10**18
        for x, y in resources:
            d = man2(nx, ny, x, y)
            if d < best:
                best = d
        return best

    best_score = -10**30
    best_move = [0, 0]
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h):
            continue
        if (nx, ny) in obs:
            continue
        if (nx, ny) == (ox, oy) and observation.get("capture_radius", 0) == 0:
            continue

        d_opp2 = man2(nx, ny, ox, oy)
        d_res2 = nearest_res_dist2(nx, ny)

        if evader:
            score = (d_opp2) - (2.0 * d_res2) - 0.01 * (dx * dx + dy * dy)
        else:
            score = (-d_opp2) - (0.2 * d_res2) - 0.01 * (dx * dx + dy * dy)

        if score > best_score or (score == best_score and [dx, dy] < best_move):
            best_score = score
            best_move = [dx, dy]

    return best_move