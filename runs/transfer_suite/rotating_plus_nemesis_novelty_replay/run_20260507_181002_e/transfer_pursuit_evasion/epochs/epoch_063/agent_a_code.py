def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0]) or [0, 0]
    ox, oy = observation.get("opponent_position", [0, 0]) or [0, 0]
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = set()
    for p in observation.get("obstacles", []) or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def clamp(x, y):
        if x < 0: x = 0
        elif x >= w: x = w - 1
        if y < 0: y = 0
        elif y >= h: y = h - 1
        return x, y

    def step(x, y, dx, dy):
        nx, ny = clamp(x + dx, y + dy)
        if (nx, ny) in obstacles:
            return x, y
        return nx, ny

    def dist2(x1, y1, x2, y2):
        dx, dy = x1 - x2, y1 - y2
        return dx * dx + dy * dy

    res_list = observation.get("resources", []) or []
    resources = []
    for r in res_list:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h:
                resources.append((x, y))
        elif isinstance(r, dict) and "x" in r and "y" in r:
            x, y = int(r["x"]), int(r["y"])
            if 0 <= x < w and 0 <= y < h:
                resources.append((x, y))

    sr = str(observation.get("self_role", "")).lower()
    orr = str(observation.get("opponent_role", "")).lower()
    evader = ("evader" in sr) or ("runner" in sr) or (("pursuer" not in sr) and ("evader" in orr))

    best = None
    best_score = None
    if resources:
        # Prefer moving toward nearest resource; break ties by avoiding opponent if evader else approaching.
        for dx, dy in moves:
            nx, ny = step(sx, sy, dx, dy)
            dres = min(dist2(nx, ny, rx, ry) for rx, ry in resources)
            dovr = dist2(nx, ny, ox, oy)
            score = dres + (0.001 * dovr if evader else -0.001 * dovr)
            if best_score is None or score < best_score:
                best_score, best = score, [dx, dy]
    else:
        # No resources: evader runs away; otherwise chase (deterministic).
        for dx, dy in moves:
            nx, ny = step(sx, sy, dx, dy)
            dovr = dist2(nx, ny, ox, oy)
            score = -dovr if evader else dovr
            if best_score is None or score > best_score:
                best_score, best = score, [dx, dy]

    return best if best is not None else [0, 0]