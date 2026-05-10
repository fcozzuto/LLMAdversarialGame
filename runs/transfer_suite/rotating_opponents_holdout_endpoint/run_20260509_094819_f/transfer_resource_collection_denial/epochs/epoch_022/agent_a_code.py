def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    resources = observation.get("resources") or []
    obstacles = observation.get("obstacles") or []
    obst = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obst.add((int(p[0]), int(p[1])))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obst

    def man(ax, ay, bx, by):
        return abs(ax - bx) + abs(ay - by)

    def pick_target():
        best = None
        for r in resources:
            if not (isinstance(r, (list, tuple)) and len(r) >= 2):
                continue
            rx, ry = int(r[0]), int(r[1])
            if not inb(rx, ry):
                continue
            sd = man(sx, sy, rx, ry)
            od = man(ox, oy, rx, ry)
            adv = od - sd
            # Prefer biggest advantage; tie-break by closer to us.
            key = (adv, -sd, -rx, -ry)
            if best is None or key > best[0]:
                best = (key, rx, ry, sd, od)
        if best is None:
            return None
        return best[1], best[2], best[3], best[4]

    target = pick_target()
    if target is None:
        return [0, 0]
    tx, ty, _, _ = target

    if sx == tx and sy == ty:
        return [0, 0]

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best_move = (None, None, None)
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        sd2 = man(nx, ny, tx, ty)
        # Opponent best-case toward target: evaluate from their greedy step.
        ndx = 0 if ox == tx else (1 if tx > ox else -1)
        ndy = 0 if oy == ty else (1 if ty > oy else -1)
        if inb(ox + ndx, oy + ndy):
            od2 = man(ox + ndx, oy + ndy, tx, ty)
        else:
            od2 = man(ox, oy, tx, ty)

        adv2 = od2 - sd2
        # Primary: advantage for target; secondary: closer to target; tertiary: deterministic tie by delta order.
        score = (adv2, -sd2, -dx, -dy)
        if best_move[0] is None or score > best_move[0]:
            best_move = (score, dx, dy)

    if best_move[1] is None:
        return [0, 0]
    return [int(best_move[1]), int(best_move[2])]