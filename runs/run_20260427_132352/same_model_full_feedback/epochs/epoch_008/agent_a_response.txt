def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [w - 1, h - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    obst = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if inb(x, y):
                obst.add((x, y))

    resources = []
    for r in observation.get("resources") or []:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if inb(x, y) and (x, y) not in obst:
                resources.append((x, y))

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0:
            dx = -dx
        dy = y1 - y2
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    if not inb(sx, sy):
        return [0, 0]

    best_target = None
    best_val = None
    # Target value: prefer resources where we are closer than opponent (and still nearby).
    for x, y in resources:
        d1 = cheb(sx, sy, x, y)
        d2 = cheb(ox, oy, x, y)
        val = (d2 - d1) * 100 - d1  # large weight to beat opponent for contested resources
        if best_val is None or val > best_val or (val == best_val and (x, y) < best_target):
            best_val = val
            best_target = (x, y)

    if best_target is None:
        # No visible resources: step to reduce distance to center while avoiding obstacles.
        tx, ty = (w - 1) // 2, (h - 1) // 2
        best_move, best_score = [0, 0], None
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not inb(nx, ny) or (nx, ny) in obst:
                continue
            score = -cheb(nx, ny, tx, ty)
            if best_score is None or score > best_score:
                best_score = score
                best_move = [dx, dy]
        return best_move

    tx, ty = best_target
    # One-step plan: choose move that most improves distance to chosen target,
    # with obstacle and "opp-cut" penalties (avoid moving into squares that make opponent much closer).
    best_move, best_score = [0, 0], None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obst:
            continue
        d_self = cheb(nx, ny, tx, ty)
        d_opp = cheb(ox, oy, tx, ty)
        opp_gain = (d_opp - d_self)
        score = -d_self + (opp_gain * 2)
        # Encourage not handing opponent an easier contested approach to another nearby resource.
        for rx, ry in resources:
            # small local check: only near resources of the target vicinity
            if cheb(tx, ty, rx, ry) > 2:
                continue
            d1n = cheb(nx, ny, rx, ry)
            d2n = cheb(ox, oy, rx, ry)
            score -= 3 if d2n - d1n > 1 else 0
        if best_score is None or score > best_score or (score == best_score and (dx, dy) < tuple(best_move)):
            best_score = score
            best_move = [dx, dy]

    return best_move