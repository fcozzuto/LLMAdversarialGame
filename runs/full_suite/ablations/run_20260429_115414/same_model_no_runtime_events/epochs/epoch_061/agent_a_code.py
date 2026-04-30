def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [w - 1, h - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for p in observation.get("resources") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def valid(nx, ny):
        return 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    # Strategy change: do not target globally; instead step that (a) beats opponent on a promising resource,
    # (b) keeps distance from opponent, and (c) avoids dead-ends via a simple neighbor count heuristic.
    best = (-(10**18), 0, 0)
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue

        opp_dist = cheb(nx, ny, ox, oy)
        # Neighbor openness (prefer positions with more options)
        open_cnt = 0
        for ddx, ddy in moves:
            tx, ty = nx + ddx, ny + ddy
            if valid(tx, ty):
                open_cnt += 1

        # Resource competition score: maximize over resources a margin where we arrive not later than opponent.
        best_margin = -10**9
        best_r = None
        for rx, ry in resources:
            d_me = cheb(nx, ny, rx, ry)
            d_op = cheb(ox, oy, rx, ry)
            margin = d_op - d_me  # positive means we are closer to that resource than opponent currently
            # slight preference for moving toward resources (smaller absolute distance)
            tieb = -d_me
            if margin > best_margin or (margin == best_margin and (tieb, -rx - ry) > (-cheb(ox, oy, rx, ry), -rx - ry)):
                best_margin = margin
                best_r = (rx, ry)

        # If no resources, just run to maximize distance while staying open.
        if not resources:
            score = (opp_dist * 2 + open_cnt)
        else:
            rx, ry = best_r
            # Encourage moving toward the chosen resource, and strongly discourage letting opponent get closer.
            d_me_here = cheb(nx, ny, rx, ry)
            d_op_here = cheb(ox, oy, rx, ry)
            score = (best_margin * 10 + opp_dist * 2 - d_me_here + open_cnt)

        # Deterministic tie-break: prefer smaller (dx,dy) lexicographically after score
        if score > best[0] or (score == best[0] and (dx, dy) < (best[1], best[2])):
            best = (score, dx, dy)

    return [int(best[1]), int(best[2])]