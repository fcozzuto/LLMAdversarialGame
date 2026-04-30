def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    me = observation.get("self_position", [0, 0]) or [0, 0]
    opp = observation.get("opponent_position", [0, 0]) or [0, 0]
    sx, sy = int(me[0]), int(me[1])
    ox, oy = int(opp[0]), int(opp[1])

    obstacles = set()
    for p in observation.get("obstacles", []) or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for r in observation.get("resources", []) or []:
        if r and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0:
            dx = -dx
        dy = ay - by
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    def legal(nx, ny):
        return 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles

    if not resources:
        tx, ty = w // 2, h // 2
    else:
        best = None
        best_key = None
        for rx, ry in resources:
            dme = cheb(sx, sy, rx, ry)
            do = cheb(ox, oy, rx, ry)
            # Prefer resources we can reach earlier; otherwise still prefer larger gap.
            key = (-(do - dme), dme, -(rx + ry), rx, ry)
            if best is None or key < best_key:
                best = (rx, ry)
                best_key = key
        tx, ty = best

    dxs = (-1, 0, 1)
    dys = (-1, 0, 1)
    moves = []
    for dx in dxs:
        for dy in dys:
            nx, ny = sx + dx, sy + dy
            if legal(nx, ny):
                d_to = cheb(nx, ny, tx, ty)
                d_opp = cheb(nx, ny, ox, oy)
                d_opp0 = cheb(sx, sy, ox, oy)
                # Prefer approaching target; also avoid moving closer to opponent if it doesn't help.
                key = (d_to, -d_opp, 0 if (d_to == cheb(sx, sy, tx, ty)) else 1, d_opp0 - d_opp, nx, ny)
                moves.append((key, dx, dy))
    if not moves:
        return [0, 0]
    moves.sort(key=lambda t: t[0])
    _, dx, dy = moves[0]
    return [int(dx), int(dy)]