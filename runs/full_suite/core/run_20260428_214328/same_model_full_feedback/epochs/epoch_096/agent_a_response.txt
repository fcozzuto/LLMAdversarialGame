def choose_move(observation):
    w = observation.get("grid_width") or 8
    h = observation.get("grid_height") or 8
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
        if dx < 0:
            dx = -dx
        dy = y1 - y2
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    def ok(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def pick_target():
        if not resources:
            return ((w - 1) if sx < w - 1 else 0, (h - 1) if sy < h - 1 else 0)
        best_t = resources[0]
        best_s = -10**9
        for rx, ry in resources:
            d_me = cheb(sx, sy, rx, ry)
            d_op = cheb(ox, oy, rx, ry)
            # Prefer resources where we are closer than opponent; otherwise prioritize nearest.
            score = (d_op - d_me) * 10 - d_me
            # Deterministic slight bias to move toward our half (away from opponent corner).
            score += (rx < w/2) != (ox < w/2)
            score += (ry < h/2) != (oy < h/2)
            if score > best_s:
                best_s = score
                best_t = (rx, ry)
        return best_t

    tx, ty = pick_target()

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    moves.sort()
    best_m = (0, 0)
    best_v = -10**18
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not ok(nx, ny):
            continue
        d_me = cheb(nx, ny, tx, ty)
        d_op = cheb(nx, ny, ox, oy)
        # Also avoid stepping into opponent range (encourage spacing).
        v = -d_me * 3 + d_op * 0.6
        # If target is now reachable, strongly prefer it.
        if cheb(nx, ny, tx, ty) == 0:
            v += 1000
        if v > best_v:
            best_v = v
            best_m = (dx, dy)
    return [int(best_m[0]), int(best_m[1])]