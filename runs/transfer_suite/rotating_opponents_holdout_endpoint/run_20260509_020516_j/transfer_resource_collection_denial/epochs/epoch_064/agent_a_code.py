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

    # Target: prefer resources where we are at least as close as opponent; otherwise pick smallest opponent distance.
    best_key = None
    tx = ty = None
    for rx, ry in resources:
        ds = man(sx, sy, rx, ry)
        do = man(ox, oy, rx, ry)
        prefer = 1 if ds <= do else 0
        adv = do - ds  # positive => we are closer
        # Deterministic tie-break: prefer closer target and lower coordinates
        key = (prefer, adv, -ds, -(rx + ry), -max(ds, do), rx, ry)
        if best_key is None or key > best_key:
            best_key = key
            tx, ty = rx, ry

    best_move = [0, 0]
    best_score = None
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            if not (0 <= nx < w and 0 <= ny < h):
                continue
            if (nx, ny) in obstacles:
                continue
            ds2 = man(nx, ny, tx, ty)
            do2 = man(ox, oy, tx, ty)
            adv2 = do2 - ds2
            # Prefer increasing advantage and reducing distance to target; slight bias away from opponent to reduce denial pressure.
            score = (adv2 * 1000) - (ds2 * 10) - (man(nx, ny, ox, oy) * 1)
            if best_score is None or score > best_score or (score == best_score and (dx, dy) < (best_move[0], best_move[1])):
                best_score = score
                best_move = [dx, dy]

    if best_score is None:
        return [0, 0]
    return best_move