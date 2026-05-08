def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0]) or [0, 0]
    ox, oy = observation.get("opponent_position", [0, 0]) or [0, 0]
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = set()
    for p in observation.get("obstacles", []) or []:
        if isinstance(p, (list, tuple)) and len(p) == 2:
            obstacles.add((int(p[0]), int(p[1])))

    resources = []
    for p in observation.get("resources", []) or []:
        if isinstance(p, (list, tuple)) and len(p) == 2:
            resources.append((int(p[0]), int(p[1])))

    sr = str(observation.get("self_role", "")).lower()
    orr = str(observation.get("opponent_role", "")).lower()
    self_is_evader = ("evader" in sr) or ("runner" in sr) or (("pursuer" not in sr) and ("evader" in orr))

    moves = [(0, 0), (1, 1), (1, 0), (1, -1), (0, 1), (0, -1), (-1, 1), (-1, 0), (-1, -1)]

    def free(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def md(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    def best_res_sign(nx, ny, want_far):
        if not resources:
            return 0
        dmin = None
        for rx, ry in resources:
            if free(rx, ry) or (rx, ry) not in obstacles:
                d = md(nx, ny, rx, ry)
                if dmin is None or d < dmin:
                    dmin = d
        if dmin is None:
            return 0
        return dmin if want_far else -dmin

    want_far = self_is_evader
    best = None
    best_key = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not free(nx, ny):
            continue
        dist = md(nx, ny, ox, oy)
        res_score = best_res_sign(nx, ny, want_far=False)
        # Key: primary maximize/minimize dist; secondary prefer resources; tertiary deterministic tie-break
        primary = dist if want_far else -dist
        key = (primary, res_score, 0, dx, dy)
        if best_key is None or key > best_key:
            best_key = key
            best = [dx, dy]
    return best if best is not None else [0, 0]