def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            px, py = int(p[0]), int(p[1])
            if 0 <= px < w and 0 <= py < h:
                obstacles.add((px, py))

    resources = []
    for r in observation.get("resources") or []:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            rx, ry = int(r[0]), int(r[1])
            if 0 <= rx < w and 0 <= ry < h and (rx, ry) not in obstacles:
                resources.append((rx, ry))

    if not resources:
        return [0, 0]

    def md(ax, ay, bx, by):
        return abs(ax - bx) + abs(ay - by)

    best = None
    for rx, ry in resources:
        dself = md(sx, sy, rx, ry)
        dopp = md(ox, oy, rx, ry)
        # Prefer resources we can reach earlier; then closer.
        key = (dopp - dself, -dself, -(rx + ry))
        if best is None or key > best[0]:
            best = (key, (rx, ry))
    tx, ty = best[1]

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    # Deterministic preference order via fixed move list; score by resulting distance/priority.
    bestm = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h):
            continue
        if (nx, ny) in obstacles:
            continue
        dself2 = md(nx, ny, tx, ty)
        # Re-evaluate advantage for this local step (still based on target).
        dself_now = md(sx, sy, tx, ty)
        dself2_adv = dself_now - dself2  # positive is improvement
        dopt2 = md(ox, oy, tx, ty)
        keym = (dself2_adv, -(dself2), -(abs(nx - tx) + abs(ny - ty)), dx, dy)
        if bestm is None or keym > bestm[0]:
            bestm = (keym, [dx, dy])

    return bestm[1] if bestm else [0, 0]