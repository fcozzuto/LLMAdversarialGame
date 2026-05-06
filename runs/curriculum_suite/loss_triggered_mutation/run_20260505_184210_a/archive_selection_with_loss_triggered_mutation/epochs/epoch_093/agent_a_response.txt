def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or (0, 0)
    op = observation.get("opponent_position") or (w - 1, h - 1)
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for r in observation.get("resources") or []:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def man(ax, ay, bx, by):
        return abs(ax - bx) + abs(ay - by)

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    # Counter-sweep: prefer resources that are simultaneously good for us and less accessible to opponent.
    if resources:
        best_val = None
        tx = ty = None
        for rx, ry in resources:
            d_self = man(sx, sy, rx, ry)
            d_opp = man(ox, oy, rx, ry)
            # Encourage "far from opponent" while still reachable.
            val = (d_opp * 2 - d_self) + (-(rx + ry) if (rx + ry) % 2 == (sx + sy) % 2 else 0)
            if best_val is None or val > best_val or (val == best_val and (rx, ry) < (tx, ty)):
                best_val = val
                tx, ty = rx, ry
    else:
        tx, ty = (w - 1) - sx, (h - 1) - sy
        tx = max(0, min(w - 1, tx))
        ty = max(0, min(h - 1, ty))

    best_move = (0, 0)
    best_score = None
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue
        d1 = man(nx, ny, tx, ty)
        d2 = man(ox, oy, tx, ty)
        # Prefer reducing distance to target; keep target hard for opponent.
        score = (-d1) + (d2 * 0.5)
        # Minor tie-break: avoid clustering near obstacles (deterministic).
        if score is not None:
            penalty = 0
            for ax, ay in deltas:
                xx, yy = nx + ax, ny + ay
                if inb(xx, yy) and (xx, yy) in obstacles:
                    penalty += 1
            score -= penalty * 0.05
        if best_score is None or score > best_score or (score == best_score and (dx, dy) < best_move):
            best_score = score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]