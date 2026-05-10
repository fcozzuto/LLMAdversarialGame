def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [w - 1, h - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for r in observation.get("resources") or []:
        if r and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))
    if not resources:
        return [0, 0]

    def man(ax, ay, bx, by):
        return abs(ax - bx) + abs(ay - by)

    # Pick target with earliest advantage (our distance <= opponent distance), break ties by smallest our distance.
    best = None
    for rx, ry in resources:
        ds = man(sx, sy, rx, ry)
        do = man(ox, oy, rx, ry)
        adv = do - ds  # positive means we are closer
        prefer = 1 if ds <= do else 0
        key = (prefer, adv, -max(ds, do), -(rx + ry), rx, ry)
        if best is None or key > best[0]:
            best = (key, (rx, ry))
    tx, ty = best[1]

    # Evaluate candidate moves; prefer moving onto a resource, then toward target while denying opponent.
    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    resource_set = set(resources)
    bestm = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h) or (nx, ny) in obstacles:
            nx, ny = sx, sy  # invalid move: engine keeps in place, emulate deterministically
            dx, dy = 0, 0
        on_res = 1 if (nx, ny) in resource_set else 0
        ds2 = man(nx, ny, tx, ty)
        do2 = man(ox, oy, tx, ty)
        adv2 = do2 - ds2
        key = (on_res, adv2, -ds2, -(abs(tx - nx) + abs(ty - ny)), dx, dy)
        if bestm is None or key > bestm[0]:
            bestm = (key, (dx, dy))
    dx, dy = bestm[1]
    if dx not in (-1, 0, 1) or dy not in (-1, 0, 1):
        return [0, 0]
    return [int(dx), int(dy)]