def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

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
    if not resources:
        return [0, 0]

    def cheb(ax, ay, bx, by):
        dx = abs(ax - bx)
        dy = abs(ay - by)
        return dx if dx > dy else dy

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    # Pick resource: prefer ones we can reach no later than opponent; then closer; then deterministic tie-break.
    best = None
    best_key = None
    for rx, ry in resources:
        ds = cheb(sx, sy, rx, ry)
        do = cheb(ox, oy, rx, ry)
        # do-ds: higher means we lose; so minimize (do-ds); if tie, minimize ds; then min rx, then min ry
        key = (do - ds, ds, rx, ry)
        if best_key is None or key < best_key:
            best_key = key
            best = (rx, ry)
    tx, ty = best

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best_step = None
    best_step_key = None
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        d_to_target = cheb(nx, ny, tx, ty)
        # If we can step onto a resource (engine likely removes it), reward by lower d_to_target primarily.
        # Secondarily, avoid letting opponent get closer (compare distances after our move).
        opp_d = cheb(ox, oy, tx, ty)
        step_key = (d_to_target, opp_d - d_to_target, nx, ny)
        if best_step_key is None or step_key < best_step_key:
            best_step_key = step_key
            best_step = (dx, dy)

    if best_step is None:
        return [0, 0]
    return [int(best_step[0]), int(best_step[1])]