def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sp = observation.get("self_position", [0, 0])
    op = observation.get("opponent_position", [0, 0])
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if p is not None and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for r in observation.get("resources") or []:
        if r is not None and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))
    if not resources:
        return [0, 0]

    def md(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    # Quick best-target scoring for the current position (used to guide move choice)
    best_cur = None
    best_gap = -10**9
    for rx, ry in resources:
        sd = md(sx, sy, rx, ry)
        od = md(ox, oy, rx, ry)
        gap = od - sd
        if gap > best_gap:
            best_gap = gap
            best_cur = (rx, ry)

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    # Deterministic tie-break order already fixed by list order.
    best_move = [0, 0]
    best_val = -10**18

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h):
            continue
        if (nx, ny) in obstacles:
            continue

        # Evaluate by best "race gap" we can achieve from the next position.
        # Also penalize getting too close to opponent (reduce interference).
        val = -10**18
        next_opp_d = 0
        for rx, ry in resources:
            sd = md(nx, ny, rx, ry)
            od = md(ox, oy, rx, ry)
            gap = od - sd
            if gap > val:
                val = gap
                next_opp_d = md(nx, ny, ox, oy)

        # Favor nearer close competitions and avoid stagnation.
        # If target is currently favorable, keep heading for it.
        if best_cur is not None:
            brx, bry = best_cur
            val += 0.05 * (md(ox, oy, brx, bry) - md(nx, ny, brx, bry))

        val -= 0.02 * next_opp_d

        if val > best_val:
            best_val = val
            best_move = [dx, dy]

    return best_move