def choose_move(observation):
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    resources = observation.get("resources", []) or []
    obstacles = {(p[0], p[1]) for p in (observation.get("obstacles", []) or [])}

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def legal(x, y):
        return inb(x, y) and (x, y) not in obstacles

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0:
            dx = -dx
        dy = y1 - y2
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    if not resources:
        return [0, 0]

    best_res = None
    best_key = None
    for rx, ry in resources:
        if not legal(rx, ry):
            continue
        sd = cheb(sx, sy, rx, ry)
        od = cheb(ox, oy, rx, ry)
        # Prefer resources where we arrive sooner; break ties by smaller sd, then coordinates.
        key = (sd - od, sd, rx, ry)
        if best_key is None or key < best_key:
            best_key = key
            best_res = (rx, ry)

    if best_res is None:
        return [0, 0]

    tx, ty = best_res
    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    # If we are already at the target, try to stay; otherwise pick the step that best preserves advantage.
    cur_sd = cheb(sx, sy, tx, ty)
    target_adv = cheb(ox, oy, tx, ty) - cur_sd

    best_move = [0, 0]
    best_step_key = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not legal(nx, ny):
            continue
        nd = cheb(nx, ny, tx, ty)
        nadv = cheb(ox, oy, tx, ty) - nd
        # Maximize advantage; then minimize our distance; then deterministic coordinate ordering via move index.
        step_key = (-nadv, nd, dx, dy)
        if best_step_key is None or step_key < best_step_key:
            best_step_key = step_key
            best_move = [dx, dy]

    # If all moves are illegal (shouldn't happen), don't move.
    return best_move