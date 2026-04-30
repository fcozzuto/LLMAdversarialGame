def choose_move(observation):
    W = int(observation.get("grid_width", 8))
    H = int(observation.get("grid_height", 8))
    sp = observation.get("self_position", [0, 0])
    op = observation.get("opponent_position", [W - 1, H - 1])
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

    def ok(x, y):
        return 0 <= x < W and 0 <= y < H and (x, y) not in obstacles

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0:
            dx = -dx
        dy = ay - by
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    def adj_obstacle(x, y):
        c = 0
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                if dx == 0 and dy == 0:
                    continue
                if (x + dx, y + dy) in obstacles:
                    c += 1
        return c

    def best_resource():
        if not resources:
            return ((W - 1) // 2, (H - 1) // 2)
        best = resources[0]
        best_val = -10**9
        for (rx, ry) in resources:
            d1 = cheb(sx, sy, rx, ry)
            d2 = cheb(ox, oy, rx, ry)
            # Prefer resources where we are closer than opponent.
            val = (d2 - d1) * 10 - d1
            # Tie-break: prefer upper-left-ish to keep determinism.
            if val > best_val or (val == best_val and (rx, ry) < best):
                best_val = val
                best = (rx, ry)
        return best

    tx, ty = best_resource()

    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    best_move = (0, 0)
    best_u = -10**18
    cur_d_opp = cheb(sx, sy, ox, oy)
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not ok(nx, ny):
            continue
        d_to_t = cheb(nx, ny, tx, ty)
        d_opp = cheb(nx, ny, ox, oy)
        # If we move towards opponent too much while contesting, discourage.
        opp_pressure = -2 if d_opp < cur_d_opp and d_to_t >= 1 else 0
        # Avoid tight obstacle adjacency.
        obs_pen = adj_obstacle(nx, ny)
        # Deterministic tie-breaking by lexicographic move.
        u = -d_to_t * 20 + (d_opp - cur_d_opp) * 3 + opp_pressure - obs_pen * 4
        if u > best_u or (u == best_u and (dx, dy) < best_move):
            best_u = u
            best_move = (dx, dy)
    dx, dy = best_move
    return [int(dx), int(dy)]