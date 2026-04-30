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
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for p in observation.get("resources") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    def ok(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def dist(a, b):
        ax, ay = a
        bx, by = b
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx + dy

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    if not resources:
        # No visible resources: drift away from opponent to avoid being forced into bad paths
        bestm = (0, 0)
        bestv = -10**9
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not ok(nx, ny):
                continue
            v = dist((nx, ny), (ox, oy))
            if v > bestv:
                bestv = v
                bestm = (dx, dy)
        return [int(bestm[0]), int(bestm[1])]

    # Target choice: prioritize resources where we're closer AND opponent is farther.
    # Use deterministic tie-break: smallest (mydist - oppdist/2, mydist, x, y).
    best = None
    best_key = None
    mypos = (sx, sy)
    opppos = (ox, oy)
    for rx, ry in resources:
        rpos = (rx, ry)
        d1 = dist(mypos, rpos)
        d2 = dist(opppos, rpos)
        key = (d1 - d2 // 2, d1, rx, ry)
        if best_key is None or key < best_key:
            best_key = key
            best = rpos

    tx, ty = best
    # Next move: go greedily toward target, but if blocked, pick best "progress" move.
    bestm = (0, 0)
    bestv = -10**9
    curd = dist(mypos, (tx, ty))
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not ok(nx, ny):
            continue
        nd = dist((nx, ny), (tx, ty))
        # Prefer reducing distance; also slightly prefer increasing distance from opponent (deny pickup races).
        v = (curd - nd) * 100 + (dist((nx, ny), opppos) - dist(mypos, opppos))
        # Deterministic tie-break: prefer lexicographically smaller move delta.
        if v > bestv or (v == bestv and (dx, dy) < bestm):
            bestv = v
            bestm = (dx, dy)
    return [int(bestm[0]), int(bestm[1])]