def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    blocked = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                blocked.add((x, y))

    resources = []
    for r in observation.get("resources") or []:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in blocked:
                resources.append((x, y))
    if not resources:
        return [0, 0]

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in blocked

    moves = [(-1,-1),(-1,0),(-1,1),(0,-1),(0,0),(0,1),(1,-1),(1,0),(1,1)]

    # Choose a deterministic target: maximize how much closer we are than opponent (deny when possible).
    best_r = None
    best_val = None
    for r in resources:
        rd, od = cheb(sx, sy, r[0], r[1]), cheb(ox, oy, r[0], r[1])
        val = (od - rd, -rd, r[0], r[1])  # lexicographic: deny first, then closer, then stable tie-break
        if best_val is None or val > best_val:
            best_val = val
            best_r = r

    tx, ty = best_r
    target_inhand = (sx == tx and sy == ty)

    # Evaluate one-step move by expected "lead" after moving, and immediate pickup.
    best_move = (0, 0)
    best_score = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        d_self = cheb(nx, ny, tx, ty)
        d_opp = cheb(ox, oy, tx, ty)
        pickup = 1 if (nx, ny) == (tx, ty) else 0

        # Also consider leaving target and stealing any other resource in range immediately.
        steal_bonus = 0
        for r in resources:
            if cheb(nx, ny, r[0], r[1]) == 0:
                steal_bonus = 2  # immediate collect trumps everything nearby

        score = (pickup, d_opp - d_self, -d_self, steal_bonus, -(abs(nx - tx) + abs(ny - ty)), nx, ny)
        if best_score is None or score > best_score:
            best_score = score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]