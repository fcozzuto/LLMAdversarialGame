def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position") or (0, 0)
    op = observation.get("opponent_position") or (w - 1, h - 1)
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for r in observation.get("resources") or []:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))
    if not resources:
        return [0, 0]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def edge_dist(x, y):
        return min(x, y, w - 1 - x, h - 1 - y)

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    near_edge = 1 if edge_dist(ox, oy) <= 1 else 0

    best_move = (0, 0)
    best_val = -10**18
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue
        # Greedy toward nearest resource, but avoid opponent and (when opponent is edge-ish) prefer interior.
        md = 10**9
        for rx, ry in resources:
            d = cheb(nx, ny, rx, ry)
            if d < md:
                md = d
        oppd = cheb(nx, ny, ox, oy)
        interior_bonus = edge_dist(nx, ny) * (1.2 if near_edge else 0.3)
        opp_avoid = oppd * (1.0 if near_edge else 0.6)
        # Slight tie-break for forward progress (reduce tendency to stall)
        stall_pen = 1 if (dx == 0 and dy == 0) else 0
        val = -md + opp_avoid + interior_bonus - 0.25 * stall_pen
        if val > best_val:
            best_val = val
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]