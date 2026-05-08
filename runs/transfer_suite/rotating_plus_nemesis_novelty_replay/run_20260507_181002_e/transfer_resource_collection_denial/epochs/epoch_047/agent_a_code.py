def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)

    def to_xy(v, default=None):
        if isinstance(v, (list, tuple)) and len(v) >= 2:
            return (int(v[0]), int(v[1]))
        if isinstance(v, dict):
            p = v.get("position", v.get("pos", None))
            if isinstance(p, (list, tuple)) and len(p) >= 2:
                return (int(p[0]), int(p[1]))
        return default

    sp = to_xy(observation.get("self_position", None), (0, 0))
    op = to_xy(observation.get("opponent_position", None), sp)
    sx, sy = sp[0], sp[1]
    ox, oy = op[0], op[1]

    obs = set()
    for o in observation.get("obstacles", []) or []:
        xy = to_xy(o, None)
        if xy is None:
            continue
        x, y = xy
        if 0 <= x < w and 0 <= y < h:
            obs.add((x, y))

    resources = []
    for r in observation.get("resources", []) or []:
        xy = to_xy(r, None)
        if xy is None:
            continue
        x, y = xy
        if 0 <= x < w and 0 <= y < h and (x, y) not in obs:
            resources.append((x, y))

    moves = []
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obs:
                moves.append((dx, dy))
    if not moves:
        return [0, 0]

    def man(a, b, c, d):
        return abs(a - c) + abs(b - d)

    # Direct advantage: pick a move that gives largest "we beat opponent" margin to some resource.
    best = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not resources:
            # Fallback: reduce own distance to opponent's start direction by aiming near opponent
            score = -(man(nx, ny, ox, oy))
            key = (score, man(nx, ny, sx, sy))
        else:
            best_adv = -10**9
            best_selfd = 10**9
            best_oppd = 10**9
            for tx, ty in resources:
                sd = man(nx, ny, tx, ty)
                od = man(ox, oy, tx, ty)
                adv = od - sd  # positive means we are closer than opponent right now
                if adv > best_adv or (adv == best_adv and (sd < best_selfd or (sd == best_selfd and od < best_oppd))):
                    best_adv, best_selfd, best_oppd = adv, sd, od
            # Encourage actually moving toward likely-taken resources: prioritize best_adv, then our distance, then opponent distance.
            key = (best_adv, -best_selfd, -best_oppd)
        cand = (key, dx, dy)
        if best is None or cand[0] > best[0]:
            best = cand

    return [int(best[1]), int(best[2])]