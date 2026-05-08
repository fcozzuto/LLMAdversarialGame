def choose_move(observation):
    w = int(observation["grid_width"])
    h = int(observation["grid_height"])
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources") or []
    obstacles = observation.get("obstacles") or []
    obs = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obs.add((x, y))
    def inb(x, y):
        return 0 <= x < w and 0 <= y < h
    def man(ax, ay, bx, by):
        return abs(ax - bx) + abs(ay - by)
    targets = []
    for r in resources:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
        elif isinstance(r, dict):
            pos = r.get("position", r.get("pos", None))
            if isinstance(pos, (list, tuple)) and len(pos) >= 2:
                x, y = int(pos[0]), int(pos[1])
            else:
                continue
        else:
            continue
        if inb(x, y) and (x, y) not in obs:
            targets.append((x, y))
    if not targets:
        return [0, 0]
    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    if (sx, sy) in obs:
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if inb(nx, ny) and (nx, ny) not in obs:
                return [dx, dy]
        return [0, 0]
    best = None
    best_key = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obs:
            continue
        my_best = 10**9
        opp_best = 10**9
        for tx, ty in targets:
            dmy = man(nx, ny, tx, ty)
            dop = man(ox, oy, tx, ty)
            if dmy < my_best:
                my_best = dmy
            if dop < opp_best:
                opp_best = dop
        key = (my_best - (opp_best * 0.35), my_best, opp_best, dx, dy)
        if best_key is None or key < best_key:
            best_key = key
            best = [dx, dy]
    return best if best is not None else [0, 0]