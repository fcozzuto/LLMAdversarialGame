def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position", [0, 0]) or [0, 0]
    op = observation.get("opponent_position", [w - 1, h - 1]) or [w - 1, h - 1]
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
    res_set = set(resources)

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0:
            dx = -dx
        dy = ay - by
        if dy < 0:
            dy = -dy
        return dx if dx >= dy else dy

    def opp_next_dist(tx, ty):
        best_d = 10**9
        best_move = (0, 0)
        for dx, dy in deltas:
            nx, ny = ox + dx, oy + dy
            if not valid(nx, ny):
                continue
            d = cheb(nx, ny, tx, ty)
            if d < best_d or (d == best_d and (dx, dy) < best_move):
                best_d = d
                best_move = (dx, dy)
        return best_d

    if not valid(sx, sy):
        return [0, 0]
    if not resources:
        return [0, 0]

    # Choose a target deterministically: closest by Chebyshev, tie by coordinates (lower first)
    best_t = None
    best_td = 10**9
    for rx, ry in resources:
        d = cheb(sx, sy, rx, ry)
        if d < best_td or (d == best_td and (rx, ry) < best_t):
            best_td = d
            best_t = (rx, ry)
    tx, ty = best_t

    best_score = -10**18
    best_delta = (0, 0)
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        d_self = cheb(nx, ny, tx, ty)
        d_opp = opp_next_dist(tx, ty)
        pick_bonus = 40 if (nx, ny) == (tx, ty) else 0
        # Prefer creating a gap: smaller self dist than opponent's next dist
        score = (d_opp - d_self) * 10 - d_self + pick_bonus
        if score > best_score or (score == best_score and (dx, dy) < best_delta):
            best_score = score
            best_delta = (dx, dy)
    return [int(best_delta[0]), int(best_delta[1])]