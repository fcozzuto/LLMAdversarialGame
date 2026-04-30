def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [w - 1, h - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obst = set()
    for p in observation.get("obstacles") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obst.add((x, y))

    resources = []
    for p in observation.get("resources") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obst:
                resources.append((x, y))

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    neigh8 = moves

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obst

    def obst_adj_pen(x, y):
        pen = 0
        for dx, dy in neigh8:
            if (x + dx, y + dy) in obst:
                pen += 1
        return pen

    if not resources:
        # No visible resources: move to increase distance from opponent while staying safe-ish.
        best = None
        best_val = -10**9
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not (0 <= nx < w and 0 <= ny < h):
                continue
            if (nx, ny) in obst:
                continue
            val = cheb(nx, ny, ox, oy) * 10 - obst_adj_pen(nx, ny) * 2
            if val > best_val:
                best_val = val
                best = (dx, dy)
        return [best[0], best[1]] if best is not None else [0, 0]

    # Score candidate moves by whether they move us closer to a resource before the opponent.
    best = (0, 0)
    best_val = -10**18
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h):
            continue
        if (nx, ny) in obst:
            continue

        my_best = -10**18
        for rx, ry in resources:
            my_d = cheb(nx, ny, rx, ry)
            op_d = cheb(ox, oy, rx, ry)
            # Prefer grabbing resources we can reach first; otherwise slight preference for blocking.
            lead = op_d - my_d  # positive if we are closer
            val = lead * 20 - my_d * 3
            if op_d == my_d:
                val -= 6
            # Encourage moving toward resources that are not adjacent to obstacles.
            val -= obst_adj_pen(nx, ny) * 1.5
            if val > my_best:
                my_best = val

        # Small tie-breaker: stay farther from opponent.
        my_best -= cheb(nx, ny, ox, oy) * 0.25
        if my_best > best_val:
            best_val = my_best
            best = (dx, dy)

    return [int(best[0]), int(best[1])]