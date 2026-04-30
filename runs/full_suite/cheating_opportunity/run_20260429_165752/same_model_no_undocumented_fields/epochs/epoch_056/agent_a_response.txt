def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    s = observation.get("self_position") or [0, 0]
    o = observation.get("opponent_position") or [0, 0]
    sx, sy = int(s[0]), int(s[1])
    ox, oy = int(o[0]), int(o[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def free(x, y):
        return inb(x, y) and (x, y) not in obstacles

    if not free(sx, sy):
        sx, sy = 0, 0
        if not free(sx, sy):
            return [0, 0]

    resources = []
    for p in observation.get("resources") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if free(x, y):
                resources.append((x, y))

    if (sx, sy) in resources:
        return [0, 0]

    def dist(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0:
            dx = -dx
        dy = ay - by
        if dy < 0:
            dy = -dy
        return dx + dy

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    # Choose best resource by advantage: smaller (dist_self - dist_opp) is better.
    target = None
    best = None
    for rx, ry in resources:
        ds = dist(sx, sy, rx, ry)
        do = dist(ox, oy, rx, ry)
        adv = ds - do
        # tie-breakers: prefer closer absolute distance and farther from opponent
        score = (adv, ds, -do)
        if best is None or score < best:
            best = score
            target = (rx, ry)

    # If no resources, drift toward center of the board (deterministic contesting).
    if target is None:
        target = (w // 2, h // 2)

    tx, ty = target
    best_move = (0, 0)
    best_val = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not free(nx, ny):
            continue
        # Evaluate move: progress to target, and avoid giving opponent too much advantage.
        ds2 = dist(nx, ny, tx, ty)
        do2 = dist(ox, oy, tx, ty)
        # Also penalize stepping onto any resource that opponent can grab immediately.
        opp_can_grab = 0
        for rx, ry in resources:
            if dist(ox, oy, rx, ry) == 1 and (nx, ny) != (rx, ry):
                opp_can_grab += 1 if (rx, ry) == (tx, ty) else 0
        val = (ds2 + 2 * (do2 - ds2), abs(nx - tx) + abs(ny - ty), -nx - ny + opp_can_grab)
        if best_val is None or val < best_val:
            best_val = val
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]