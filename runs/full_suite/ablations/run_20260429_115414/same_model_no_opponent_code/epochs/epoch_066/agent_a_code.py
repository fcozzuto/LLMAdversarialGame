def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0]) or [0, 0]
    ox, oy = observation.get("opponent_position", [w - 1, h - 1]) or [w - 1, h - 1]
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = set()
    for p in observation.get("obstacles", []) or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for p in observation.get("resources", []) or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    def king(a, b):
        ax, ay = a
        bx, by = b
        dx = ax - bx
        if dx < 0:
            dx = -dx
        dy = ay - by
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    me = (sx, sy)
    opp = (ox, oy)
    if not resources:
        return [0, 0]

    best_r = resources[0]
    best_val = -10**18
    for r in resources:
        myd = king(me, r)
        opd = king(opp, r)
        val = (opd - myd) * 1000 - myd
        if val > best_val:
            best_val = val
            best_r = r

    target = best_r
    move_order = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    best_move = (0, 0)
    best_cost = 10**18
    best_opp = -10**18
    for dx, dy in move_order:
        nx, ny = sx + dx, sy + dy
        if nx < 0 or nx >= w or ny < 0 or ny >= h:
            continue
        if (nx, ny) in obstacles:
            continue
        nd = king((nx, ny), target)
        od = king((nx, ny), opp)
        cost = nd * 10 + (0 if (dx == 0 and dy == 0) else 0)
        if cost < best_cost or (cost == best_cost and od > best_opp):
            best_cost = cost
            best_opp = od
            best_move = (dx, dy)

    if best_move == (0, 0):
        # If somehow all moves are blocked, must stay.
        return [0, 0]
    return [int(best_move[0]), int(best_move[1])]