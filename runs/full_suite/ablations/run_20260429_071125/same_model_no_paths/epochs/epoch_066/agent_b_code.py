def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    blocked = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                blocked.add((x, y))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in blocked

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    resources = []
    for r in observation.get("resources") or []:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if inb(x, y):
                resources.append((x, y))

    dirs = [(0, 0), (1, 0), (-1, 0), (0, 1), (0, -1), (1, 1), (1, -1), (-1, 1), (-1, -1)]
    legal = []
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if inb(nx, ny):
            legal.append((dx, dy))
    if not legal:
        return [0, 0]

    if resources:
        best = None
        best_val = -10**18
        for rx, ry in resources:
            ds = cheb(sx, sy, rx, ry)
            do = cheb(ox, oy, rx, ry)
            lead = do - ds  # positive means we are closer
            # Favor capture races; break ties by preferring closer (smaller ds), then deterministic order
            val = 10 * lead - ds
            if lead <= 0:
                val -= 2  # discourage targets we likely lose
            if val > best_val:
                best_val = val
                best = (rx, ry)
        tx, ty = best
    else:
        # No resources: drift toward center while keeping distance from opponent slightly
        tx, ty = (w - 1) // 2, (h - 1) // 2

    best_move = (0, 0)
    best_score = -10**18
    for dx, dy in legal:
        nx, ny = sx + dx, sy + dy
        d_to_t = cheb(nx, ny, tx, ty)
        d_op = cheb(nx, ny, ox, oy)
        d_op_curr = cheb(sx, sy, ox, oy)
        # Prefer reducing distance to target; lightly avoid moving closer to opponent unless it also improves target race
        score = -d_to_t
        if resources:
            ds_now = cheb(sx, sy, tx, ty)
            do_now = cheb(ox, oy, tx, ty)
            ds_next = d_to_t
            do_next = cheb(ox, oy, tx, ty)
            score += 3 * ((do_next - ds_next) - (do_now - ds_now))
        score += 0.05 * (d_op - d_op_curr)
        # deterministic tie-break by move ordering
        if score > best_score:
            best_score = score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]