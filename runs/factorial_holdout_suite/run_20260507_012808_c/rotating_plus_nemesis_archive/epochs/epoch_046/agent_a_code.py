def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w, h = int(observation["grid_width"]), int(observation["grid_height"])
    resources = observation.get("resources") or []
    obstacles = observation.get("obstacles") or []

    obs = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obs.add((x, y))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obs

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    free_res = []
    for r in resources:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obs:
                free_res.append((x, y))

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    if free_res:
        bestt = None
        bestd = 10**9
        for tx, ty in free_res:
            d = cheb(sx, sy, tx, ty)
            if d < bestd or (d == bestd and (tx, ty) < bestt):
                bestd = d
                bestt = (tx, ty)
        tx, ty = bestt
        best_move = (0, 0)
        best_score = None
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not inb(nx, ny):
                continue
            d_to_t = cheb(nx, ny, tx, ty)
            d_opp = cheb(nx, ny, ox, oy)
            # minimize distance to target; maximize distance from opponent; deterministic tie
            score = (d_to_t, -d_opp, nx, ny)
            if best_score is None or score < best_score:
                best_score = score
                best_move = (dx, dy)
        return [best_move[0], best_move[1]]

    # No resources visible: move toward nearest free corner deterministically
    corners = [(0, 0), (w - 1, 0), (0, h - 1), (w - 1, h - 1)]
    corners = [c for c in corners if inb(c[0], c[1])]
    if not corners:
        return [0, 0]
    tx, ty = min(corners, key=lambda c: (cheb(sx, sy, c[0], c[1]), c[0], c[1]))
    best_move = (0, 0)
    bestd = 10**9
    bestpos = (sx, sy)
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        d = cheb(nx, ny, tx, ty)
        if d < bestd or (d == bestd and (nx, ny) < bestpos):
            bestd = d
            bestpos = (nx, ny)
            best_move = (dx, dy)
    return [best_move[0], best_move[1]]