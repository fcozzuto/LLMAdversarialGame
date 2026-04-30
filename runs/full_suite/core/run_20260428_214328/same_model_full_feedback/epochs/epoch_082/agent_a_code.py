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

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx + dy

    def ok(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def best_target(px, py, qx, qy):
        if not resources:
            return (w - 1 - qx) if w else (w // 2), (h - 1 - qy) if h else (h // 2)
        best = None
        best_key = None
        for tx, ty in resources:
            sd = cheb(px, py, tx, ty)
            od = cheb(qx, qy, tx, ty)
            key = (od - sd, -sd, -cheb(tx, ty, (w - 1) // 2, (h - 1) // 2))
            if best_key is None or key > best_key:
                best_key = key
                best = (tx, ty)
        return best

    tx, ty = best_target(sx, sy, ox, oy)

    # Score candidate moves: move closer to target; also prefer moves that keep opponent farther.
    best_move = (0, 0)
    best_score = -10**18
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not ok(nx, ny):
            continue
        d_self = cheb(nx, ny, tx, ty)
        d_opp = cheb(ox, oy, tx, ty)
        # Our advantage if we can get closer than opponent (approx).
        opp_after = max(0, d_opp - 1)  # deterministic slight bias
        adv = opp_after - d_self
        # Safety: avoid stepping adjacent to obstacles too often
        safe = 0
        for ox2, oy2 in obstacles:
            if cheb(nx, ny, ox2, oy2) <= 1:
                safe -= 1
        score = (adv * 1000) - d_self * 10 + safe
        if score > best_score:
            best_score = score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]