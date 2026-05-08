def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)

    def get_xy(v, default=(0, 0)):
        if isinstance(v, (list, tuple)) and len(v) >= 2:
            return (int(v[0]), int(v[1]))
        if isinstance(v, dict):
            p = v.get("position", v.get("pos", None))
            if isinstance(p, (list, tuple)) and len(p) >= 2:
                return (int(p[0]), int(p[1]))
        return default

    sx, sy = get_xy(observation.get("self_position", None), (0, 0))
    ox, oy = get_xy(observation.get("opponent_position", None), (sx, sy))

    obstacles = set()
    for o in observation.get("obstacles", []) or []:
        x, y = get_xy(o, (None, None))
        if x is None:
            continue
        if 0 <= x < w and 0 <= y < h:
            obstacles.add((x, y))

    def in_bounds(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    resources = []
    for r in observation.get("resources", []) or []:
        x, y = get_xy(r, (None, None))
        if x is None:
            continue
        if in_bounds(x, y):
            resources.append((x, y))

    candidates = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    opp_d = lambda x, y: abs(x - ox) + abs(y - oy)
    self_d = lambda x, y: abs(x - sx) + abs(y - sy)

    if not resources:
        for dx, dy in [(0, 0), (1, 0), (0, 1), (-1, 0), (0, -1), (1, 1), (-1, -1), (1, -1), (-1, 1)]:
            nx, ny = sx + dx, sy + dy
            if in_bounds(nx, ny):
                return [dx, dy]
        return [0, 0]

    def best_target_score(tx, ty):
        sd = self_d(tx, ty)
        od = opp_d(tx, ty)
        return (od - sd, -od, -sd)  # prioritize resources we can reach first

    tx, ty = max(resources, key=lambda p: best_target_score(p[0], p[1]))

    step_dx = 0 if tx == sx else (1 if tx > sx else -1)
    step_dy = 0 if ty == sy else (1 if ty > sy else -1)

    direct = [(step_dx, step_dy), (step_dx, 0), (0, step_dy), (0, 0)]
    best_move = (0, 0)
    best_val = (-10**18, 0, 0)
    for dx, dy in direct + candidates:
        if not in_bounds(sx + dx, sy + dy):
            continue
        nx, ny = sx + dx, sy + dy
        sd = self_d(nx, ny)
        od = opp_d(nx, ny)
        val = (od - sd, -sd, -od)
        if val > best_val:
            best_val = val
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]