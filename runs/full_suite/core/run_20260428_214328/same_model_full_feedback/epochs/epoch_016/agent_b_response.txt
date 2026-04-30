def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position", [0, 0]) or [0, 0]
    op = observation.get("opponent_position", [0, 0]) or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles", []) or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for p in observation.get("resources", []) or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0:
            dx = -dx
        dy = y1 - y2
        if dy < 0:
            dy = -dy
        return dx if dx >= dy else dy

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    best_res = None
    best_gap = -10**18
    if resources:
        for rx, ry in resources:
            sd = cheb(sx, sy, rx, ry)
            od = cheb(ox, oy, rx, ry)
            gap = od - sd  # want resources opponent is farther from than us
            if gap > best_gap or (gap == best_gap and (sd < cheb(sx, sy, *(best_res or (0, 0))))):
                best_gap = gap
                best_res = (rx, ry)

    tx, ty = (best_res if best_res is not None else ((w - 1) // 2, (h - 1) // 2))

    # If opponent is already closer to everything, drift to break symmetry: prefer farthest from opponent among remaining resources
    if resources:
        mind_self = 10**9
        mind_opp = 10**9
        for rx, ry in resources:
            mind_self = min(mind_self, cheb(sx, sy, rx, ry))
            mind_opp = min(mind_opp, cheb(ox, oy, rx, ry))
        if mind_opp < mind_self:
            far_res = None
            far_sc = -10**18
            for rx, ry in resources:
                sc = cheb(ox, oy, rx, ry) - cheb(sx, sy, rx, ry)
                if sc > far_sc:
                    far_sc = sc
                    far_res = (rx, ry)
            tx, ty = far_res

    # Choose move that best improves our distance to target while keeping away from opponent and avoiding obstacles
    best_move = (0, 0)
    best_val = -10**18
    cur_sd = cheb(sx, sy, tx, ty)
    cur_od = cheb(sx, sy, ox, oy)
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue
        nd = cheb(nx, ny, tx, ty)
        no = cheb(nx, ny, ox, oy)
        # prioritize reaching target; then keep distance from opponent; then avoid stagnation
        val = (cur_sd - nd) * 1000 + (no - cur_od) * 3 - nd
        if val > best_val:
            best_val = val
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]