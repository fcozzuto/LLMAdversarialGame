def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obs = set()
    for p in observation.get("obstacles", []) or []:
        if p is not None and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obs.add((x, y))

    resources = []
    for r in observation.get("resources", []) or []:
        if r is not None and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obs:
                resources.append((x, y))

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    if resources:
        best = None
        best_key = None
        for rx, ry in resources:
            sd = cheb(sx, sy, rx, ry)
            od = cheb(ox, oy, rx, ry)
            # Prefer resources where we are closer (od - sd large), then prefer being closer (sd small), then deterministic.
            key = (od - sd, -sd, -(rx + 17 * ry))
            if best_key is None or key > best_key:
                best_key = key
                best = (rx, ry)
        tx, ty = best
    else:
        tx, ty = (w - 1) // 2, (h - 1) // 2

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    cur_d = cheb(sx, sy, tx, ty)
    best_move = (0, 0)
    best_val = None

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h):
            continue
        if (nx, ny) in obs:
            continue
        nd = cheb(nx, ny, tx, ty)
        # If we can, prefer reducing distance; otherwise keep still. Also discourage moves that let opponent close too quickly.
        opp_now = cheb(ox, oy, tx, ty)
        opp_next = cheb(ox + (1 if ox < tx else -1 if ox > tx else 0), oy + (1 if oy < ty else -1 if oy > ty else 0), tx, ty)
        val = (-(nd - cur_d), -(opp_next - opp_now), -(nx + 13 * ny))
        if best_val is None or val > best_val:
            best_val = val
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]