def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
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

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def ok(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    cx, cy = (w - 1) // 2, (h - 1) // 2

    def score_move(nx, ny):
        if resources:
            # Prefer resources we're closer to; if not, try to reduce opponent lead.
            best = None
            for rx, ry in resources:
                ds = cheb(nx, ny, rx, ry)
                do = cheb(ox, oy, rx, ry)
                if do <= 0:
                    continue
                # Base: go to nearest resource by our distance
                key = ds
                # Bonus if we are at least as good as opponent on that resource
                lead = do - ds
                # Stronger if it flips advantage; mild if just competitive
                adjust = -3.0 * lead
                # Discourage stepping away from all resources
                val = key * 10.0 + adjust
                if best is None or val < best:
                    best = val
            if best is None:
                best = cheb(nx, ny, cx, cy) * 2.0
            return best
        else:
            # No resources: drift toward center / reduce distance to opponent slightly (avoid being cornered)
            return cheb(nx, ny, cx, cy) * 1.0 + cheb(nx, ny, ox, oy) * 0.1

    best_move = (0, 0)
    best_val = None
    # Deterministic tie-break: prefer moves closer to opponent's position less, then lexicographically by (dx,dy)
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not ok(nx, ny):
            continue
        v = score_move(nx, ny)
        if best_val is None or v < best_val:
            best_val = v
            best_move = (dx, dy)
        elif v == best_val:
            cand_op = cheb(nx, ny, ox, oy)
            best_op = cheb(sx + best_move[0], sy + best_move[1], ox, oy)
            if cand_op < best_op or (cand_op == best_op and (dx, dy) < best_move):
                best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]