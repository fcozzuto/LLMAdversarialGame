def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sx, sy = observation.get("self_position") or [0, 0]
    ox, oy = observation.get("opponent_position") or [w - 1, h - 1]
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    def to_set(key):
        s = set()
        for p in observation.get(key) or []:
            if p and len(p) >= 2:
                x, y = int(p[0]), int(p[1])
                if 0 <= x < w and 0 <= y < h:
                    s.add((x, y))
        return s

    resources = to_set("resources")
    unclaimed = to_set("unclaimed_cells")

    def dist2(ax, ay, bx, by):
        dx = ax - bx
        dy = ay - by
        return dx * dx + dy * dy

    # Deterministic target: nearest resource, else nearest unclaimed, else center
    tx = ty = None
    best = 10**18
    if resources:
        for x, y in sorted(resources):
            d = dist2(sx, sy, x, y)
            if d < best:
                best, tx, ty = d, x, y
    elif unclaimed:
        for x, y in sorted(unclaimed):
            d = dist2(sx, sy, x, y)
            if d < best:
                best, tx, ty = d, x, y
    else:
        tx, ty = w // 2, h // 2

    neigh = [(-1, 0), (1, 0), (0, -1), (0, 1), (-1, -1), (-1, 1), (1, -1), (1, 1), (0, 0)]

    def ok(nx, ny):
        return 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles

    best_move = (0, 0)
    best_score = -10**18
    for dx, dy in neigh:
        nx, ny = sx + dx, sy + dy
        if not ok(nx, ny):
            continue
        d_target = dist2(nx, ny, tx, ty)
        d_opp = dist2(nx, ny, ox, oy)
        move_score = -d_target + (0.05 * d_opp)
        if resources and (nx, ny) in resources:
            move_score += 10**6
        if unclaimed and (nx, ny) in unclaimed:
            move_score += 10**3
        # Tie-break deterministically: prefer smaller (dx,dy) tuple
        if move_score > best_score or (move_score == best_score and (dx, dy) < best_move):
            best_score = move_score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]