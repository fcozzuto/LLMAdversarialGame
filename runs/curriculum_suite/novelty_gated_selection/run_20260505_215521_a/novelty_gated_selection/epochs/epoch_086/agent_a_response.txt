def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obst = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obst.add((int(p[0]), int(p[1])))

    resources = []
    for r in observation.get("resources") or []:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            resources.append((int(r[0]), int(r[1])))

    if not resources:
        return [0, 0]

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def dist_cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def dist_manh(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx + dy

    # Pick a target that is good for us but relatively bad for the opponent (deny).
    best_target = resources[0]
    best_score = -10**18
    for rx, ry in resources:
        ds = dist_cheb(sx, sy, rx, ry)
        do = dist_cheb(ox, oy, rx, ry)
        # Closer to us is good; closer to opponent is bad; tie-break by lower manhattan for determinism.
        score = (-ds) + 0.6 * do
        tie = -dist_manh(sx, sy, rx, ry) * 1e-3
        score2 = score + tie
        if score2 > best_score:
            best_score = score2
            best_target = (rx, ry)

    rx, ry = best_target

    # Evaluate immediate move: move closer to target, avoid obstacles, and optionally pressure opponent.
    best_move = (0, 0)
    best_val = -10**18
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obst:
            continue
        dself = dist_cheb(nx, ny, rx, ry)
        dop = dist_cheb(nx, ny, ox, oy)
        # Pressure term: prefer moves that get closer to opponent only if it doesn't sacrifice target pursuit.
        val = (-dself) + 0.12 * dop
        # If we can directly "challenge" by reducing their distance to our target, slightly prefer.
        if dist_cheb(ox, oy, rx, ry) <= dself:
            val += 0.15
        # Deterministic tie-break: prefer staying on same row, then same column, then lexicographic.
        val += (0.000001 if dx == 0 else 0) + (0.0000001 if dy == 0 else 0) - (abs(dx) + abs(dy)) * 1e-7
        if val > best_val:
            best_val = val
            best_move = (dx, dy)

    # If all moves invalid (surrounded by obstacles/out of bounds), stay.
    return [int(best_move[0]), int(best_move[1])]