def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
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

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obst

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    if not resources:
        # Fallback: drift toward center while avoiding obstacles deterministically
        tx, ty = (w - 1) // 2, (h - 1) // 2
        best = (10**9, (0, 0))
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not valid(nx, ny): 
                continue
            d = cheb(nx, ny, tx, ty)
            if d < best[0] or (d == best[0] and (nx, ny) < (sx + best[1][0], sy + best[1][1])):
                best = (d, (dx, dy))
        return [best[1][0], best[1][1]]

    best_move = (0, 0)
    best_val = -10**18

    # Choose move that maximizes advantage for claiming resources quickly
    # Value combines (opponent distance - self distance) and self closeness.
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        # Tie-break deterministically by (nx,ny)
        val = -10**18
        for rx, ry in resources:
            d_me = cheb(nx, ny, rx, ry)
            d_op = cheb(ox, oy, rx, ry)
            # Encourage picking a resource where we are (or become) closer than opponent
            advantage = (d_op - d_me)  # positive is good
            # Prefer nearer resources overall (smaller d_me)
            v = advantage * 50 - d_me
            if v > val:
                val = v
        if val > best_val or (val == best_val and (nx, ny) < (sx + best_move[0], sy + best_move[1])):
            best_val = val
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]