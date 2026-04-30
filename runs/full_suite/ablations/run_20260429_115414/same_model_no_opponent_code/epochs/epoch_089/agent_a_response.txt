def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [w - 1, h - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in (observation.get("obstacles") or []):
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for p in (observation.get("resources") or []):
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def dman(ax, ay, bx, by):
        return abs(ax - bx) + abs(ay - by)

    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    best_move = (0, 0)
    best_val = -10**18

    opp_d = dman(sx, sy, ox, oy)
    toward_bias = 0.0
    if resources:
        # Choose a target resource deterministically: closest; tie -> lexicographically smallest.
        target = None
        tkey = None
        for rx, ry in resources:
            k = (dman(sx, sy, rx, ry), rx, ry)
            if tkey is None or k < tkey:
                tkey = k
                target = (rx, ry)
        tx, ty = target
        toward_bias = 1.0

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue

        if resources:
            mind = 10**9
            near_cnt = 0
            for rx, ry in resources:
                dd = dman(nx, ny, rx, ry)
                if dd < mind:
                    mind = dd
                    near_cnt = 1
                elif dd == mind:
                    near_cnt += 1
            nd_opp = dman(nx, ny, ox, oy)

            # Strategy: sprint to nearest resource while avoiding opponent contact/race.
            # Also add a small deterministic tie-break for moving toward chosen target.
            tstep = 0
            if toward_bias:
                tstep = -dman(nx, ny, tx, ty)  # higher is better

            val = (-1000 * mind) + (20 * nd_opp) + (1 if near_cnt == 1 else 0) + (0.5 * tstep)
        else:
            # If no resources listed, just keep away from opponent while staying in bounds.
            val = (5 * dman(nx, ny, ox, oy)) - (0.1 * dman(nx, ny, w - 1, h - 1))

        if val > best_val:
            best_val = val
            best_move = (dx, dy)
        elif val == best_val:
            # Deterministic tie-break: prefer moves with smaller step index then smaller dx/dy.
            order = {d: i for i, d in enumerate(dirs)}
            if order[(dx, dy)] < order[best_move]:
                best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]