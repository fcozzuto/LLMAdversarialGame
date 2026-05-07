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
            px, py = int(p[0]), int(p[1])
            if 0 <= px < w and 0 <= py < h:
                obstacles.add((px, py))

    resources = []
    for r in observation.get("resources") or []:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            rx, ry = int(r[0]), int(r[1])
            if 0 <= rx < w and 0 <= ry < h and (rx, ry) not in obstacles:
                resources.append((rx, ry))

    if not resources:
        return [0, 0]

    def md(ax, ay, bx, by):
        return abs(ax - bx) + abs(ay - by)

    # Prioritize resources we can reach first; otherwise pick ones where opponent is much slower.
    best = None
    best_t = resources[0]
    for rx, ry in resources:
        ds = md(sx, sy, rx, ry)
        do = md(ox, oy, rx, ry)
        margin = do - ds
        if ds <= do:
            key = (1, margin, -ds, -rx - 3 * ry, -rx)
        else:
            key = (0, -ds, margin, -rx - 3 * ry, -rx)  # strongly prefer large negative margin (opp much slower)
        if best is None or key > best:
            best = key
            best_t = (rx, ry)
    tx, ty = best_t

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best_move = (0, 0)
    best_key = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h):
            continue
        if (nx, ny) in obstacles:
            continue
        if (nx, ny) == (ox, oy):
            continue  # avoid stepping onto opponent position
        d_to_target = md(nx, ny, tx, ty)
        d_opp = md(nx, ny, ox, oy)
        # Avoid oscillation: prefer moves that reduce distance to target and don't move closer to opponent too much.
        key = (-d_to_target, d_opp, -(dx * dx + dy * dy), -abs(nx - tx) - abs(ny - ty))
        if best_key is None or key > best_key:
            best_key = key
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]