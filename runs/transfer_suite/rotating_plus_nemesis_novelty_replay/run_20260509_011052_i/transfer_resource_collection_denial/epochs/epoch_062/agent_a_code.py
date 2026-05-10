def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or (0, 0)
    op = observation.get("opponent_position") or (0, 0)
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    blocked = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                blocked.add((x, y))

    resources = []
    for p in observation.get("resources") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in blocked:
                resources.append((x, y))

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0:
            dx = -dx
        dy = ay - by
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    if not resources:
        return [0, 0]

    best = None
    best_key = None
    for x, y in resources:
        self_d = cheb(sx, sy, x, y)
        opp_d = cheb(ox, oy, x, y)
        # Prefer being closer; break ties by being quicker (smaller self_d), then by coordinate.
        key = (opp_d - self_d, -min(self_d, opp_d), -self_d, -x, -y)
        if best_key is None or key > best_key:
            best_key = key
            best = (x, y)

    tx, ty = best

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    cur_self = cheb(sx, sy, tx, ty)
    cur_opp = cheb(ox, oy, tx, ty)

    best_move = [0, 0]
    best_move_key = None
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h):
            continue
        if (nx, ny) in blocked:
            continue
        ns = cheb(nx, ny, tx, ty)
        no = cur_opp  # opponent position unchanged this move
        # Maximize progress and advantage; deterministic tie-break by fixed ordering.
        key = (cur_self - ns, (no - ns), -ns, -dx, -dy)
        if best_move_key is None or key > best_move_key:
            best_move_key = key
            best_move = [dx, dy]

    return best_move