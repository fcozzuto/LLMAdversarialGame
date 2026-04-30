def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
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
    for r in observation.get("resources") or []:
        if r and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    def legal(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0:
            dx = -dx
        dy = y1 - y2
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    if not legal(sx, sy):
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if legal(nx, ny):
                return [dx, dy]
        return [0, 0]

    best = (None, 10**9, -10**9)  # (target, our_dist, diff)
    any_safe = False
    for rx, ry in resources:
        d1 = cheb(sx, sy, rx, ry)
        d2 = cheb(ox, oy, rx, ry)
        diff = d2 - d1  # positive means we are earlier
        if d1 == 0:
            return [0, 0]
        if diff >= 0:
            any_safe = True
            # prioritize: earlier (diff), then closer (d1), then deterministic tie-break
            cand = (diff, -d1, rx + 7 * ry)
            if (best[0] is None) or (cand > (best[2], -best[1], best[0][0] + 7 * best[0][1])):
                best = ((rx, ry), d1, diff)
        elif not any_safe:
            cand = (diff, -d1, rx + 7 * ry)
            if (best[0] is None) or (cand > (best[2], -best[1], best[0][0] + 7 * best[0][1])):
                best = ((rx, ry), d1, diff)

    tx, ty = (sx, sy) if best[0] is None else best[0]

    # Greedy step toward target; if blocked, choose best alternative toward target while avoiding self-slowing.
    best_moves = []
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not legal(nx, ny):
            continue
        d = cheb(nx, ny, tx, ty)
        # slight repulsion from opponent to change policy vs prior "direct pursuit"
        od = cheb(nx, ny, ox, oy)
        score = (d, -od, dx * 3 - dy)  # deterministic tie-break via dx/dy
        best_moves.append((score, dx, dy))
    if not best_moves:
        return [0, 0]
    best_moves.sort(key=lambda z: z[0])
    return [best_moves[0][1], best_moves[0][2]]