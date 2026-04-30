def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [w - 1, h - 1])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for p in observation.get("resources") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    moves.sort()

    if not resources:
        tx, ty = ((w - 1, h - 1) if cheb(sx, sy, w - 1, h - 1) <= cheb(ox, oy, w - 1, h - 1) else (0, 0))
        tx, ty = int(tx), int(ty)
    else:
        tx, ty = resources[0]

    best_move = (0, 0)
    best_val = -10**18

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue

        d_res = 10**9
        if resources:
            for rx, ry in resources:
                d = cheb(nx, ny, rx, ry)
                if d < d_res:
                    d_res = d

        d_opp = cheb(nx, ny, ox, oy)
        d_me = cheb(nx, ny, sx, sy)

        # Prefer reaching resources, keep closer to opponent when resources are scarce, avoid giving up.
        if not resources:
            val = -cheb(nx, ny, tx, ty) * 1000 - d_opp * 2 + (1 if d_me == 1 else 0)
        else:
            val = -d_res * 50 - d_opp * 8 + (1 if (nx, ny) in resources else 0)

        if val > best_val:
            best_val = val
            best_move = [dx, dy]

    return [int(best_move[0]), int(best_move[1])]