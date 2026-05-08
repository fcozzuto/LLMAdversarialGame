def choose_move(observation):
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))

    def to_xy(obj):
        if isinstance(obj, (list, tuple)) and len(obj) == 2:
            return int(obj[0]), int(obj[1])
        if isinstance(obj, dict):
            q = obj.get("position", obj.get("pos", None))
            if isinstance(q, (list, tuple)) and len(q) == 2:
                return int(q[0]), int(q[1])
        return None

    obs_set = set()
    for p in observation.get("obstacles", []) or []:
        t = to_xy(p)
        if t is not None:
            obs_set.add(t)

    resources = []
    for r in observation.get("resources", []) or []:
        t = to_xy(r)
        if t is not None:
            resources.append(t)

    def in_bounds(x, y):
        return 0 <= x < w and 0 <= y < h

    if not resources:
        return [0, 0]

    dirs8 = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best = None
    best_key = None

    for tx, ty in resources:
        sd = abs(tx - sx) + abs(ty - sy)
        od = abs(tx - ox) + abs(ty - oy)
        # Intercept bias: maximize opponent distance lead; if none, contest by minimizing opponent distance.
        key = (od - sd, -sd, -od, tx, ty)
        if best_key is None or key > best_key:
            best_key = key
            best = (tx, ty)

    tx, ty = best

    # Prefer a move that most reduces our distance to target, while not stepping into obstacles.
    best_move = [0, 0]
    best_score = None
    for dx, dy in dirs8:
        nx, ny = sx + dx, sy + dy
        if not in_bounds(nx, ny) or (nx, ny) in obs_set:
            continue
        nsd = abs(tx - nx) + abs(ty - ny)
        nod = abs(tx - ox) + abs(ty - oy)
        # also slightly prefer moves that keep us ahead vs opponent to the same target
        score = (-nsd, (nod - nsd), dx, dy)
        if best_score is None or score > best_score:
            best_score = score
            best_move = [dx, dy]

    return [int(best_move[0]), int(best_move[1])]