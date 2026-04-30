def choose_move(observation):
    W = int(observation.get("grid_width") or 8)
    H = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [W - 1, H - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < W and 0 <= y < H:
                obstacles.add((x, y))

    resources = []
    for p in observation.get("resources") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < W and 0 <= y < H and (x, y) not in obstacles:
                resources.append((x, y))

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def inb(x, y):
        return 0 <= x < W and 0 <= y < H and (x, y) not in obstacles

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    legal = []
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if inb(nx, ny):
            legal.append((dx, dy))
    if not legal:
        return [0, 0]

    if resources:
        best = None
        best_score = None
        for rx, ry in resources:
            ds = cheb(sx, sy, rx, ry)
            do = cheb(ox, oy, rx, ry)
            # Prefer resources we can reach sooner; slightly discourage chasing resources where we are slower.
            score = ds - 0.85 * do + 0.02 * cheb(sx, sy, rx, ry)  # deterministic tie-break scaling
            if best_score is None or score < best_score:
                best_score = score
                best = (rx, ry)
        tx, ty = best
        # Choose move that advances toward target while maintaining/increasing distance from opponent.
        bestm = None
        bestms = None
        for dx, dy in legal:
            nx, ny = sx + dx, sy + dy
            ds = cheb(nx, ny, tx, ty)
            sep = cheb(nx, ny, ox, oy)
            # Primary: reduce distance to target; Secondary: increase separation; Tertiary: prefer staying within bounds handled by legal.
            ms = ds * 3.0 - sep
            if bestms is None or ms < bestms:
                bestms = ms
                bestm = (dx, dy)
        return [int(bestm[0]), int(bestm[1])]

    # No visible resources: drift to a corner away from opponent deterministically.
    target = (0, 0)
    if ox + oy < (W - 1) + (H - 1) - (ox + oy):
        target = (W - 1, H - 1)
    else:
        target = (0, H - 1) if ox <= oy else (W - 1, 0)
    tx, ty = target

    bestm = None
    bestms = None
    for dx, dy in legal:
        nx, ny = sx + dx, sy + dy
        ds = cheb(nx, ny, tx, ty)
        sep = cheb(nx, ny, ox, oy)
        ms = ds - 0.5 * sep
        if bestms is None or ms < bestms:
            bestms = ms
            bestm = (dx, dy)
    return [int(bestm[0]), int(bestm[1])]