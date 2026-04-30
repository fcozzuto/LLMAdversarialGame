def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position", [0, 0]) or [0, 0]
    op = observation.get("opponent_position", [0, 0]) or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])
    obstacles = observation.get("obstacles", []) or []
    resources = observation.get("resources", []) or []

    blocked = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                blocked.add((x, y))

    res = []
    for r in resources:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in blocked:
                res.append((x, y))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def md(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    def cheb(x1, y1, x2, y2):
        dx = abs(x1 - x2)
        dy = abs(y1 - y2)
        return dx if dx > dy else dy

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    cx, cy = (w - 1) // 2, (h - 1) // 2

    if not res:
        best = (0, 0)
        bestv = -10**9
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not inb(nx, ny) or (nx, ny) in blocked:
                continue
            v = -cheb(nx, ny, cx, cy)
            if v > bestv:
                bestv, best = v, (dx, dy)
        return [best[0], best[1]]

    # Choose move by best "advantage" to a chosen resource (who is closer).
    # Deterministic: tie-break by larger advantage then smaller self distance then smaller dx,dy.
    best_move = (0, 0)
    best_score = -10**18
    best_selfd = 10**9

    for dxm, dym in moves:
        nx, ny = sx + dxm, sy + dym
        if not inb(nx, ny) or (nx, ny) in blocked:
            continue
        best_for_this = -10**18
        best_for_this_selfd = 10**9
        for rx, ry in res:
            ds = md(nx, ny, rx, ry)
            do = md(ox, oy, rx, ry)
            # Prefer targets we can reach sooner; if opponent is closer, still move to disrupt by reducing their lead.
            advantage = (do - ds)
            # Small secondary term: encourage moving toward the resource while also slightly toward the center.
            score = advantage * 1000 - ds * 3 - cheb(nx, ny, cx, cy)
            if (score > best_for_this) or (score == best_for_this and ds < best_for_this_selfd):
                best_for_this = score
                best_for_this_selfd = ds
        if (best_for_this > best_score) or (best_for_this == best_score and best_for_this_selfd < best_selfd) or (
            best_for_this == best_score and best_for_this_selfd == best_selfd and (dxm, dym) < best_move
        ):
            best_score = best_for_this
            best_selfd = best_for_this_selfd
            best_move = (dxm, dym)

    return [int(best_move[0]), int(best_move[1])]