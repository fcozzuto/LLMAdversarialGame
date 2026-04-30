def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [w - 1, h - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for p in observation.get("resources") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))
    if not resources:
        return [0, 0]

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def blocked(x, y):
        return not (0 <= x < w and 0 <= y < h) or (x, y) in obstacles

    # Choose target: maximize advantage (opponent farther than us), then prefer earliest/closer, tie-break deterministically.
    best = None
    best_key = None
    for rx, ry in resources:
        ds = cheb(sx, sy, rx, ry)
        do = cheb(ox, oy, rx, ry)
        # advantage first; then smaller ds; then prefer higher remaining_resource_count bias (more remaining -> earlier capture)
        key = (do - ds, -ds, -((rx + ry) & 1), rx, ry)
        if best_key is None or key > best_key:
            best_key = key
            best = (rx, ry)

    tx, ty = best

    # Move one step toward target, avoiding obstacles; if multiple, pick deterministic best.
    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    cur_best = None
    cur_key = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if blocked(nx, ny):
            continue
        ds_next = cheb(nx, ny, tx, ty)
        # discourage moves that give opponent a better shot at the same target
        do_next = cheb(ox, oy, tx, ty)
        # small bias to keep movement stable and deterministic
        step_key = (-(ds_next), -(((nx + ny) & 1)), -abs(dx), -abs(dy))
        if cur_key is None or step_key > cur_key:
            cur_key = step_key
            cur_best = (dx, dy)

    if cur_best is None:
        # All adjacent blocked; stay.
        return [0, 0]
    return [int(cur_best[0]), int(cur_best[1])]