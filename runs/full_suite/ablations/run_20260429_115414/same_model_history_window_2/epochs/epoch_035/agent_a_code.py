def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    blocked = set()
    for p in observation.get("obstacles") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                blocked.add((x, y))

    resources = []
    for r in observation.get("resources") or []:
        if r and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in blocked:
                resources.append((x, y))

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def ok(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in blocked

    if resources:
        best_val = None
        best_move = (0, 0)
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not ok(nx, ny):
                continue
            my_d = cheb(nx, ny, ox, oy)
            # Evaluate the best resource from the hypothetical next position.
            # Prefer: getting a resource sooner; deprioritize resources closer to opponent.
            val = -10**9
            for rx, ry in resources:
                d_self = cheb(nx, ny, rx, ry)
                d_opp = cheb(ox, oy, rx, ry)
                # Strongly prefer capturing before opponent when close.
                # Also prefer reducing distance to nearest resource overall.
                v = (-2.0 * d_self) + (1.2 * d_opp) + (0.35 * my_d) - (0.02 * d_self * d_self)
                if v > val:
                    val = v
            # Deterministic tie-break: lexicographic over move.
            if best_val is None or val > best_val or (val == best_val and (dx, dy) < best_move):
                best_val = val
                best_move = (dx, dy)
        return [int(best_move[0]), int(best_move[1])]

    # No resources visible: deterministically drift toward center while keeping away from opponent.
    cx, cy = (w - 1) / 2.0, (h - 1) / 2.0
    target = (int(round(cx)), int(round(cy)))
    best_val = None
    best_move = (0, 0)
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not ok(nx, ny):
            continue
        d_center = cheb(nx, ny, target[0], target[1])
        d_opp = cheb(nx, ny, ox, oy)
        val = (0.9 * d_opp) - (1.0 * d_center)
        if best_val is None or val > best_val or (val == best_val and (dx, dy) < best_move):
            best_val = val
            best_move = (dx, dy)
    return [int(best_move[0]), int(best_move[1])]