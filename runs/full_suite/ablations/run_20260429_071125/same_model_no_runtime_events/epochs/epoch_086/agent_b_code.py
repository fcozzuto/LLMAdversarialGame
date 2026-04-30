def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
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

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def chebd(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0:
            dx = -dx
        dy = y1 - y2
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    resources = []
    for r in observation.get("resources") or []:
        if r and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if valid(x, y):
                resources.append((x, y))

    # Choose target by maximizing "being closer than opponent" advantage.
    target = None
    best_adv = None
    for (tx, ty) in resources:
        sd = chebd(sx, sy, tx, ty)
        od = chebd(ox, oy, tx, ty)
        adv = od - sd
        if target is None or adv > best_adv or (adv == best_adv and (sd < chebd(sx, sy, target[0], target[1]) or (sd == chebd(sx, sy, target[0], target[1]) and (tx, ty) < target))):
            target = (tx, ty)
            best_adv = adv

    # If no resources or no positive advantage, go to nearest resource; else keep advantage target.
    if target is None:
        tx, ty = ox, oy
    else:
        if best_adv is not None and best_adv <= 0 and resources:
            target = min(resources, key=lambda t: (chebd(sx, sy, t[0], t[1]), t[0], t[1]))
        tx, ty = target[0], target[1]

    # Greedy step: minimize our distance to target; tie-break by maximizing advantage at the next step.
    best_move = (0, 0)
    best_score = None
    cur_sd = chebd(sx, sy, tx, ty)
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        nsd = chebd(nx, ny, tx, ty)
        nod = chebd(ox, oy, tx, ty)
        adv_next = nod - nsd
        score = (nsd, -adv_next, abs(dx) + abs(dy))
        if best_score is None or score < best_score:
            best_score = score
            best_move = (dx, dy)

    # If somehow stuck (no valid moves), stay.
    if best_score is None:
        return [0, 0]
    return [best_move[0], best_move[1]]