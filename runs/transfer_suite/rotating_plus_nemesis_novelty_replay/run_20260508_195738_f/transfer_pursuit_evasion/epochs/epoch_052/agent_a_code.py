def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    try:
        sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)
    except:
        sx, sy, ox, oy = 0, 0, 0, 0

    obs_set = set()
    for p in observation.get("obstacles", []) or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obs_set.add((x, y))
    obs_list = list(obs_set)

    self_role = str(observation.get("self_role", "") or "").lower()
    opp_role = str(observation.get("opponent_role", "") or "").lower()
    evader = ("evad" in self_role) or (("agent" in self_role) and ("evad" in opp_role))

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    def legal(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obs_set

    def dist2(a, b, c, d):
        dx, dy = a - c, b - d
        return dx * dx + dy * dy

    def min_obs_dist2(x, y):
        md = None
        for ax, ay in obs_list:
            d2 = (x - ax) * (x - ax) + (y - ay) * (y - ay)
            if md is None or d2 < md:
                md = d2
        return md if md is not None else 10_000

    best_move = [0, 0]
    best_score = None

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not legal(nx, ny):
            continue
        if evader:
            score = -dist2(nx, ny, ox, oy) + 0.05 * min_obs_dist2(nx, ny)
        else:
            score = dist2(nx, ny, ox, oy) - 0.02 * min_obs_dist2(nx, ny)
        if best_score is None or score < best_score if not evader else score > best_score:
            best_score = score
            best_move = [dx, dy]

    if legal(sx, sy):
        return best_move if best_move != [0, 0] or any(legal(sx + dx, sy + dy) for dx, dy in dirs) else [0, 0]
    return [0, 0]