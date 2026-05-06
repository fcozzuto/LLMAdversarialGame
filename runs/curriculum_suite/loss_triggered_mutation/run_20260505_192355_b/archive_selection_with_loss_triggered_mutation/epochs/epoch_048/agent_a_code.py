def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = observation.get("obstacles", []) or []
    obst = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obst.add((x, y))

    resources = observation.get("resources", []) or []
    res = []
    for r in resources:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obst:
                res.append((x, y))

    def free(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obst

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    if not free(sx, sy):
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if free(nx, ny):
                return [dx, dy]
        return [0, 0]

    best_target = None
    best_score = -10**18

    def dist(a, b):
        ax, ay = a
        bx, by = b
        return abs(ax - bx) + abs(ay - by)

    for tx, ty in res:
        sd = dist((sx, sy), (tx, ty))
        od = dist((ox, oy), (tx, ty))
        score = (od - sd) * 100 - sd
        score += 3 if (ty == oy and abs(tx - ox) <= 2) else 0  # slightly prioritize resources on opponent row
        if score > best_score:
            best_score = score
            best_target = (tx, ty)

    if best_target is None:
        # No reachable resources; head toward opponent's current row to deny sweep
        ty = oy
        tx = sx
        if free(sx + (1 if ox > sx else -1 if ox < sx else 0), ty):
            dx = 1 if ox > sx else -1 if ox < sx else 0
            dy = 0
            return [dx, dy]
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if free(nx, ny) and ny == ty:
                return [dx, dy]
        return [0, 0]

    tx, ty = best_target
    if (sx, sy) == (tx, ty):
        return [0, 0]

    desired_dx = 0 if tx == sx else (1 if tx > sx else -1)
    desired_dy = 0 if ty == sy else (1 if ty > sy else -1)

    candidates = []
    for dx, dy in [(desired_dx, desired_dy), (desired_dx, 0), (0, desired_dy), (0, 0)]:
        nx, ny = sx + dx, sy + dy
        if (dx, dy) != (0, 0) and not free(nx, ny):
            continue
        if free(nx, ny):
            candidates.append((dist((nx, ny), (tx, ty)), dx, dy))

    # If diagonal/primary step blocked, pick any move that greedily reduces distance to target
    if not candidates:
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if free(nx, ny):
                candidates.append((dist((nx, ny), (tx, ty)), dx, dy))

    candidates.sort(key=lambda t: (t[0], t[1], t[2]))
    return [int(candidates[0][1]), int(candidates[0][2])]