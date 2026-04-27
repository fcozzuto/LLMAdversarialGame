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

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    cx, cy = (w - 1) / 2.0, (h - 1) / 2.0

    # Pick a target resource where we are (or can become) earlier than the opponent.
    best_t = None
    best_val = -10**18
    for rx, ry in resources:
        ds = cheb(sx, sy, rx, ry)
        do = cheb(ox, oy, rx, ry)
        v = (do - ds) * 10 - ds + 0.15 * (cheb(sx, sy, cx, cy) - cheb(rx, ry, cx, cy))
        # If opponent is closer, still consider it if it's a big "trap" (small gap) and we can at least contest.
        if ds == 0:
            v += 10000
        if v > best_val:
            best_val = v
            best_t = (rx, ry)

    if best_t is None:
        # Fallback: deterministic drift toward center while keeping clear of obstacles locally.
        tx, ty = cx, cy
    else:
        tx, ty = best_t[0], best_t[1]

    # Move scoring: prefer reducing distance to target; if contesting, also slightly prefer increasing opponent's distance.
    best_move = (0, 0)
    best_move_val = -10**18
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        d_to_t = cheb(nx, ny, int(tx), int(ty))
        d_opp = cheb(nx, ny, ox, oy)
        base = -d_to_t * 3 + (cheb(ox, oy, int(tx), int(ty)) - d_to_t) * 2 - d_opp * 0.05
        # Small tie-breaker: move that gets us off our current cell when possible.
        if (dx, dy) != (0, 0) and (d_to_t < cheb(sx, sy, int(tx), int(ty))):
            base += 0.25
        if base > best_move_val:
            best_move_val = base
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]