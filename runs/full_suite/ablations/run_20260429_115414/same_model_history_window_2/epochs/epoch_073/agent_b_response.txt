def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [w - 1, h - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    blocked = set()
    for b in observation.get("obstacles") or []:
        if b and len(b) >= 2:
            bx, by = int(b[0]), int(b[1])
            if 0 <= bx < w and 0 <= by < h:
                blocked.add((bx, by))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in blocked

    resources = []
    for r in observation.get("resources") or []:
        if r and len(r) >= 2:
            rx, ry = int(r[0]), int(r[1])
            if inb(rx, ry):
                resources.append((rx, ry))

    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0:
            dx = -dx
        dy = y1 - y2
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    def best_target():
        if not resources:
            return None
        best = None
        best_val = 10**18
        for rx, ry in resources:
            md = cheb(sx, sy, rx, ry)
            od = cheb(ox, oy, rx, ry)
            val = md - 1.3 * od  # prioritize resources I'm relatively closer to
            if val < best_val:
                best_val = val
                best = (rx, ry)
        return best

    target = best_target()
    best_move = (0, 0)
    best_score = -10**18

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue

        if target is not None:
            tx, ty = target
            dist_to_t = cheb(nx, ny, tx, ty)
            dist_to_opp = cheb(nx, ny, ox, oy)
            # avoid getting into opponent's capture neighborhood while rushing target
            adj_opp_pen = 0.0
            if dist_to_opp <= 1:
                adj_opp_pen = 3.0
            # slight preference to reduce my distance while increasing opponent distance to the same target
            opp_dist_to_t_next = cheb(ox, oy, tx, ty)
            score = (-1.8 * dist_to_t) + (0.35 * dist_to_opp) - adj_opp_pen + (0.15 * opp_dist_to_t_next)
        else:
            cx, cy = w // 2, h // 2
            dist_center = cheb(nx, ny, cx, cy)
            dist_to_opp = cheb(nx, ny, ox, oy)
            score = (-1.0 * dist_center) + (0.4 * dist_to_opp)

        if score > best_score:
            best_score = score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]