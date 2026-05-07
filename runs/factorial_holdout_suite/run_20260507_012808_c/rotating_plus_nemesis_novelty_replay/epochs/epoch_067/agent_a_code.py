def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    sx = int(sx); sy = int(sy); ox = int(ox); oy = int(oy)

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if p and len(p) >= 2:
            x = int(p[0]); y = int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for r in observation.get("resources") or []:
        if r and len(r) >= 2:
            x = int(r[0]); y = int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    if (sx, sy) in resources:
        return [0, 0]

    def dist(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx + dy

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    # Pick a resource where we are (deterministically) ahead; otherwise go to nearest.
    best = None
    best_key = None
    for rx, ry in resources:
        d_me = dist(sx, sy, rx, ry)
        d_op = dist(ox, oy, rx, ry)
        ahead = d_op - d_me  # positive means we are closer
        key = (-(ahead), d_me, rx, ry)
        if best_key is None or key < best_key:
            best_key = key
            best = (rx, ry)

    if best is None:
        # No resources known: drift toward opponent but avoid obstacles.
        tx, ty = ox, oy
    else:
        tx, ty = best

    # Choose move that stays valid and minimizes distance to target; tie-break toward diagonals.
    curd = dist(sx, sy, tx, ty)
    best_step = (0, 0)
    best_val = (10**9, 10**9, 10**9)
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h) or (nx, ny) in obstacles:
            continue
        nd = dist(nx, ny, tx, ty)
        diag = 0 if (dx == 0 or dy == 0) else 1
        step_val = (nd, -diag, abs(nx - ox) + abs(ny - oy))
        if step_val < best_val:
            best_val = step_val
            best_step = (dx, dy)

    # If all moves invalid (rare), stay.
    if best_step is None:
        return [0, 0]
    return [int(best_step[0]), int(best_step[1])]