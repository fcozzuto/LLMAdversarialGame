def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position", [0, 0]) or [0, 0]
    op = observation.get("opponent_position", [0, 0]) or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for o in observation.get("obstacles", []) or []:
        if isinstance(o, (list, tuple)) and len(o) >= 2:
            obstacles.add((int(o[0]), int(o[1])))

    resources = []
    for r in observation.get("resources", []) or []:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            rx, ry = int(r[0]), int(r[1])
            if (rx, ry) not in obstacles:
                resources.append((rx, ry))
    if not resources:
        return [0, 0]

    def in_bounds(x, y):
        return 0 <= x < w and 0 <= y < h

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0:
            dx = -dx
        dy = y1 - y2
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    moves8 = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    best = None
    best_score = None
    for tx, ty in resources:
        sd = cheb(sx, sy, tx, ty)
        od = cheb(ox, oy, tx, ty)
        # Prefer resources we can reach first; discourage giving opponent a faster path.
        score = (od - sd) * 4 - sd
        # If opponent aligned horizontally/vertically/diagonally, slightly penalize (denier-style).
        if (tx == ox or ty == oy or (tx - ox) == (ty - oy) or (tx - ox) == -(ty - oy)):
            score -= 2
        # Small deterministic preference: favor higher y then higher x.
        score += (ty * 0.01 + tx * 0.001)
        if best is None or score > best_score:
            best_score = score
            best = (tx, ty)

    tx, ty = best
    # Choose the move that most reduces distance to target without hitting obstacles/out of bounds.
    curd = cheb(sx, sy, tx, ty)
    best_step = (0, 0)
    best_step_val = None
    for dx, dy in moves8:
        nx, ny = sx + dx, sy + dy
        if not in_bounds(nx, ny):
            continue
        if (nx, ny) in obstacles:
            continue
        nd = cheb(nx, ny, tx, ty)
        # Prefer moves that reduce distance; tie-break deterministically by dx,dy.
        val = (curd - nd, -nd, -dx, -dy)
        if best_step_val is None or val > best_step_val:
            best_step_val = val
            best_step = (dx, dy)

    return [int(best_step[0]), int(best_step[1])]