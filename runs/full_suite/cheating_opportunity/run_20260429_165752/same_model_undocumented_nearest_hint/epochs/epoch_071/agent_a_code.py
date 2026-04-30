def choose_move(observation):
    W = int(observation.get("grid_width") or 8)
    H = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [W - 1, H - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < W and 0 <= y < H:
                obstacles.add((x, y))

    resources = []
    for r in observation.get("resources") or []:
        if r and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < W and 0 <= y < H and (x, y) not in obstacles:
                resources.append((x, y))

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def legal(nx, ny):
        return 0 <= nx < W and 0 <= ny < H and (nx, ny) not in obstacles

    if resources:
        best = None
        best_score = -10**9
        for rx, ry in resources:
            d_me = cheb(sx, sy, rx, ry)
            d_opp = cheb(ox, oy, rx, ry)
            # Prefer resources where we are (or become) relatively ahead; slightly prefer closer overall.
            score = (d_opp - d_me) * 20 - d_me
            if score > best_score:
                best_score = score
                best = (rx, ry)
        tx, ty = best
    else:
        tx, ty = (W - 1) // 2, (H - 1) // 2

    best_move = (0, 0)
    best_val = -10**18
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not legal(nx, ny):
            continue
        myd = cheb(nx, ny, tx, ty)
        oppd = cheb(ox, oy, tx, ty)

        # If opponent is very close to our chosen target, bias toward moves that increase their effective lead.
        # Also add a small tie-break: avoid stepping into squares that are closer to opponent than we are (when possible).
        dist_me_now = cheb(nx, ny, tx, ty)
        dist_opp_now = cheb(ox, oy, tx, ty)
        anti_lead = (dist_opp_now - dist_me_now)

        # Safety/obstacle pressure: prefer moves with more legal neighbors.
        neigh = 0
        for ddx, ddy in moves:
            mx, my = nx + ddx, ny + ddy
            if legal(mx, my):
                neigh += 1

        val = -myd * 100 + anti_lead * 25 + (oppd - myd) * 8 + neigh
        if val > best_val:
            best_val = val
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]