def choose_move(observation):
    sx, sy = int(observation["self_position"][0]), int(observation["self_position"][1])
    ox, oy = int(observation["opponent_position"][0]), int(observation["opponent_position"][1])
    w, h = int(observation.get("grid_width", 8)), int(observation.get("grid_height", 8))
    resources = observation.get("resources") or []
    obstacles = observation.get("obstacles") or []

    obst = set()
    for p in obstacles:
        try:
            obst.add((int(p[0]), int(p[1])))
        except Exception:
            pass

    def inside(x, y):
        return 0 <= x < w and 0 <= y < h

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    def dist(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    if not resources:
        # stay competitive: move toward center-away-from-opponent if possible
        tx, ty = w // 2, h // 2
        if dist((sx, sy), (ox, oy)) < dist((sx, sy), (tx, ty)):
            tx, ty = tx, ty
        dx = 0 if tx == sx else (1 if tx > sx else -1)
        dy = 0 if ty == sy else (1 if ty > sy else -1)
        nx, ny = sx + dx, sy + dy
        if inside(nx, ny) and (nx, ny) not in obst:
            return [dx, dy]
        return [0, 0]

    res = []
    for r in resources:
        try:
            rx, ry = int(r[0]), int(r[1])
            if inside(rx, ry):
                res.append((rx, ry))
        except Exception:
            pass
    if not res:
        return [0, 0]

    # pick target with maximum competitive advantage; tie-break by closer to self then lexicographic
    best = None
    for cell in res:
        sd = dist((sx, sy), cell)
        od = dist((ox, oy), cell)
        adv = od - sd
        key = (adv, -sd, -cell[1], -cell[0])
        if best is None or key > best[0]:
            best = (key, cell)

    target = best[1]

    # choose best next move: highest advantage after move, avoid obstacles, deterministic tie-break
    best_move = [0, 0]
    best_key = None
    order = moves  # fixed deterministic order
    for dx, dy in order:
        nx, ny = sx + dx, sy + dy
        if not inside(nx, ny) or (nx, ny) in obst:
            continue
        sd2 = dist((nx, ny), target)
        od2 = dist((ox, oy), target)
        adv2 = od2 - sd2
        key = (adv2, -sd2, abs((nx + ny) - (sx + sy)), -dx, -dy)
        if best_key is None or key > best_key:
            best_key = key
            best_move = [dx, dy]

    if best_key is None:
        return [0, 0]
    return best_move