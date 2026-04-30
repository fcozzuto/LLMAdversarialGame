def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0]) or [0, 0]
    ox, oy = observation.get("opponent_position", [0, 0]) or [0, 0]
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = set()
    for o in (observation.get("obstacles", []) or []):
        if o is not None and len(o) >= 2:
            x, y = int(o[0]), int(o[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for r in (observation.get("resources", []) or []):
        if r is not None and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h:
                resources.append((x, y))
    if not resources:
        return [0, 0]

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0:
            dx = -dx
        dy = ay - by
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    def blocked(x, y):
        return x < 0 or y < 0 or x >= w or y >= h or (x, y) in obstacles

    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    best_r = None
    best_val = None
    for rx, ry in resources:
        sd = cheb(sx, sy, rx, ry)
        od = cheb(ox, oy, rx, ry)
        val = (od - sd, -sd, rx, ry)  # maximize margin; then closer; deterministic tie
        if best_val is None or val > best_val:
            best_val = val
            best_r = (rx, ry)
    tx, ty = best_r

    best_move = (0, 0)
    best_eval = None
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if blocked(nx, ny):
            continue
        selfd = cheb(nx, ny, tx, ty)
        on_res = 1 if (nx, ny) in obstacles else 0  # obstacles won't contain resources, kept deterministic
        # Capture bonus if stepping onto a remaining resource location.
        cap = 1 if (nx, ny) in set(resources) else 0
        oppd = cheb(ox, oy, tx, ty)
        # Encourage reducing our distance to target and capturing; slight penalty if moving away too much.
        ev = (cap * 1000 + (oppd - selfd) * 10 - selfd * 2 - (dx == 0 and dy == 0) * 0.5, -selfd, dx, dy)
        if best_eval is None or ev > best_eval:
            best_eval = ev
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]