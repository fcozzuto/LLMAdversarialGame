def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position", [0, 0]) or [0, 0]
    op = observation.get("opponent_position", [0, 0]) or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    blocked = set()
    for p in observation.get("obstacles") or []:
        if p and len(p) >= 2:
            bx, by = int(p[0]), int(p[1])
            if 0 <= bx < w and 0 <= by < h:
                blocked.add((bx, by))

    role_s = str(observation.get("self_role", "")).lower()
    is_evader = ("evader" in role_s) or ("runner" in role_s) or ("flee" in role_s) or ("avoid" in role_s)

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def cheb(x1, y1, x2, y2):
        dx = x2 - x1
        if dx < 0:
            dx = -dx
        dy = y2 - y1
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    def free_neigh(x, y):
        cnt = 0
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                if dx == 0 and dy == 0:
                    continue
                nx, ny = x + dx, y + dy
                if inb(nx, ny) and (nx, ny) not in blocked:
                    cnt += 1
        return cnt

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    if is_evader:
        corners = [(0, 0), (0, h - 1), (w - 1, 0), (w - 1, h - 1)]
        best_corner = corners[0]
        bestd = -1
        for cx, cy in corners:
            if (cx, cy) in blocked:
                continue
            d = cheb(cx, cy, ox, oy)
            if d > bestd:
                bestd = d
                best_corner = (cx, cy)
        tx, ty = best_corner
    else:
        tx, ty = ox, oy

    best = None
    best_sc = None
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in blocked:
            sc = -10**9
        else:
            d_op = cheb(nx, ny, ox, oy)
            d_t = cheb(nx, ny, tx, ty)
            neigh = free_neigh(nx, ny)
            if is_evader:
                sc = (d_op * 1000) - (d_t * 8) + (neigh * 3)
                if d_op == 0:
                    sc = -10**8
            else:
                sc = (-d_op * 1000) - (d_t * 4) + (neigh * 3)
                if d_op == 0:
                    sc = 10**8
        if best_sc is None or sc > best_sc:
            best_sc = sc
            best = [dx, dy]

    return [int(best[0]), int(best[1])]