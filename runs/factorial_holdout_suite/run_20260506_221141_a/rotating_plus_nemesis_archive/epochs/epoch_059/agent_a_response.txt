def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [w - 1, h - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = p[0], p[1]
            if isinstance(x, int) and isinstance(y, int) and 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for r in observation.get("resources") or []:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = r[0], r[1]
            if isinstance(x, int) and isinstance(y, int) and 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))
    if not resources:
        return [0, 0]

    def dist(a, b):
        dx = abs(a[0] - b[0])
        dy = abs(a[1] - b[1])
        return dx if dx > dy else dy  # Chebyshev distance, diagonal cost 1

    best = None
    best_score = None
    for rx, ry in resources:
        my_d = dist((sx, sy), (rx, ry))
        op_d = dist((ox, oy), (rx, ry))
        # Prefer resources where we arrive earlier; otherwise still pick nearest that limits opponent lead.
        adv = op_d - my_d
        key = (adv, -my_d, rx, ry)
        if best is None or key > best_score:
            best = (rx, ry)
            best_score = key

    tx, ty = best

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    def valid(nx, ny):
        return 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles

    # Choose move that best improves our distance to target, but only among valid moves.
    best_m = (0, 0)
    best_k = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        d1 = dist((nx, ny), (tx, ty))
        d_op = dist((ox, oy), (tx, ty))
        my_lead = d_op - d1
        # Tie-break: prefer staying closer to target, then maximize lead, then deterministic order by dx,dy.
        k = (my_lead, -d1, -abs(nx - tx) - abs(ny - ty), dx, dy)
        if best_k is None or k > best_k:
            best_k = k
            best_m = (dx, dy)

    return [int(best_m[0]), int(best_m[1])]