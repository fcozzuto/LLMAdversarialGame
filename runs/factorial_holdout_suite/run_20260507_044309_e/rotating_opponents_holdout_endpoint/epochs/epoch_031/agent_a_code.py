def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)

    resources = observation.get("resources", []) or []
    obstacles_raw = observation.get("obstacles", []) or []

    res = []
    for p in resources:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            res.append((int(p[0]), int(p[1])))

    obs = set()
    for p in obstacles_raw:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obs.add((int(p[0]), int(p[1])))

    if not res:
        return [0, 0]

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obs

    dirs = [(0, 0), (1, 0), (-1, 0), (0, 1), (0, -1), (1, 1), (1, -1), (-1, 1), (-1, -1)]

    def man(a, b, c, d):
        da = a - c
        if da < 0:
            da = -da
        db = b - d
        if db < 0:
            db = -db
        return da + db

    # Pick a deterministic target: closest to us, tie by (x,y).
    target = res[0]
    best_td = man(sx, sy, target[0], target[1])
    for r in res[1:]:
        d = man(sx, sy, r[0], r[1])
        if d < best_td or (d == best_td and (r[0], r[1]) < (target[0], target[1])):
            best_td = d
            target = r

    tx, ty = target
    opp_d = man(ox, oy, tx, ty)

    best_move = [0, 0]
    best_score = -10**18

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        new_d = man(nx, ny, tx, ty)
        score = (opp_d - new_d) * 1000
        if (nx, ny) == (tx, ty):
            score += 10**6
        if score > best_score or (score == best_score and (dx, dy) < (best_move[0], best_move[1])):
            best_score = score
            best_move = [dx, dy]

    return best_move