def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
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

    def ok(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in blocked

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best = (0, 0)
    best_val = -10**18

    if not resources:
        tx, ty = (w - 1) // 2, (h - 1) // 2
        for dx, dy in dirs:
            nx, ny = sx + dx, sy + dy
            if ok(nx, ny):
                v = -cheb(nx, ny, tx, ty)
                if v > best_val:
                    best_val, best = v, (dx, dy)
        return [best[0], best[1]]

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not ok(nx, ny):
            continue
        # Evaluate best immediate target with an opponent race component.
        v = -10**12
        for rx, ry in resources:
            d_my = cheb(nx, ny, rx, ry)
            d_op = cheb(ox, oy, rx, ry)
            # If we can arrive sooner, prioritize aggressively.
            # Also prefer closer resources overall and penalize being farther than opponent.
            race = (d_op - d_my)  # positive is good
            # Capture at resource cell (d_my==0) is strongest.
            score = 0
            if d_my == 0:
                score = 10**9
            else:
                score = (race * 2000) - (d_my * 40) - (max(0, -race) * 120)
                # Small preference for mid-board to avoid corners stalling.
                score -= cheb(nx, ny, (w - 1) // 2, (h - 1) // 2)
            if score > v:
                v = score
        # If tie/close, keep deterministic order with small preference for not moving too much.
        v -= (dx*dx + dy*dy) * 2
        if v > best_val:
            best_val, best = v, (dx, dy)

    return [best[0], best[1]]