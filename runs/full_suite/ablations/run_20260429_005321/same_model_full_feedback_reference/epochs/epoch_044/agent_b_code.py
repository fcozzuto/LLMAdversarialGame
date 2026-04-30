def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [w - 1, h - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) == 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    resources = []
    for p in observation.get("resources") or []:
        if isinstance(p, (list, tuple)) and len(p) == 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def dist(a, b, c, d):
        return abs(a - c) + abs(b - d)

    def best_target():
        if not resources:
            return None
        best = None
        best_key = None
        for tx, ty in resources:
            ds = dist(sx, sy, tx, ty)
            do = dist(ox, oy, tx, ty)
            # Prefer closer to self, but also prefer positions farther from opponent.
            key = (ds - 0.7 * do, tx, ty)
            if best_key is None or key < best_key:
                best_key = key
                best = (tx, ty)
        return best

    target = best_target()
    if target is None:
        return [0, 0]
    tx, ty = target

    best_move = (0, 0)
    best_score = -10**18
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        ds_cur = dist(sx, sy, tx, ty)
        ds_new = dist(nx, ny, tx, ty)
        do_new = dist(nx, ny, ox, oy)
        # Strongly reduce distance to target, strongly avoid getting close to opponent.
        score = (ds_cur - ds_new) * 200 + do_new * 8
        # Mild tie-break: prefer moving along diagonal/heading toward target.
        score += (1 if (dx != 0 and dy != 0) else 0) * 1.5
        if score > best_score:
            best_score = score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]