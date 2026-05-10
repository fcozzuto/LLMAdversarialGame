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
            obstacles.add((int(p[0]), int(p[1])))

    self_role = (observation.get("self_role") or "").lower()
    evader = ("evad" in self_role) or ("escape" in self_role)

    def legal(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def cheb(x, y):
        dx = x - ox
        if dx < 0:
            dx = -dx
        dy = y - oy
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    corners = [(0, 0), (0, h - 1), (w - 1, 0), (w - 1, h - 1)]
    far_corner = max(corners, key=lambda c: cheb(c[0], c[1])) if evader else min(corners, key=lambda c: cheb(c[0], c[1]))

    def score_for(nx, ny):
        d = cheb(nx, ny)
        # Next-step mobility: for evader prefer more options; for pursuer prefer fewer escapes.
        cnt = 0
        for ddx, ddy in moves:
            tx, ty = nx + ddx, ny + ddy
            if legal(tx, ty):
                cnt += 1
        # Corner bias: evader wants to drift to far_corner, pursuer to drift away from it.
        bias = cheb(nx, ny) - cheb(far_corner[0], far_corner[1])
        return (d, cnt, bias)

    best_move = (0, 0)
    best = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not legal(nx, ny):
            continue
        sc = score_for(nx, ny)
        if best is None:
            best = sc
            best_move = (dx, dy)
            continue
        # Lexicographic compare with role direction.
        if evader:
            if (sc[0] > best[0]) or (sc[0] == best[0] and sc[1] > best[1]) or (sc[0] == best[0] and sc[1] == best[1] and sc[2] > best[2]):
                best = sc
                best_move = (dx, dy)
        else:
            if (sc[0] < best[0]) or (sc[0] == best[0] and sc[1] < best[1]) or (sc[0] == best[0] and sc[1] == best[1] and sc[2] < best[2]):
                best = sc
                best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]