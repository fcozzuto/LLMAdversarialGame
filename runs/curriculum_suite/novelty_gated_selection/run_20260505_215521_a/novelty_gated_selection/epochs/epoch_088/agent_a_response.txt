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

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def best_without_resources():
        bestv = -10**9
        bestm = (0, 0)
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not inb(nx, ny) or (nx, ny) in obst:
                continue
            v = cheb(nx, ny, ox, oy)
            if v > bestv:
                bestv = v
                bestm = (dx, dy)
        return [bestm[0], bestm[1]]

    if not resources:
        return best_without_resources()

    # Race heuristic: pick a resource where we gain most over opponent (chebyshev distance).
    best_r = resources[0]
    best_gain = -10**9
    for rx, ry in resources:
        du = cheb(sx, sy, rx, ry)
        do = cheb(ox, oy, rx, ry)
        gain = do - du
        if gain > best_gain:
            best_gain = gain
            best_r = (rx, ry)

    tx, ty = best_r

    # Move toward target while staying valid; prefer reducing distance, tie-break by increasing opponent separation.
    best_score = -10**9
    bestm = (0, 0)
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obst:
            continue
        du2 = cheb(nx, ny, tx, ty)
        sep = cheb(nx, ny, ox, oy)
        # Primary: minimize distance-to-target; Secondary: maximize separation from opponent.
        score = (-du2 * 1000) + sep
        if score > best_score:
            best_score = score
            bestm = (dx, dy)

    # Fallback if all moves invalid
    return [bestm[0], bestm[1]]