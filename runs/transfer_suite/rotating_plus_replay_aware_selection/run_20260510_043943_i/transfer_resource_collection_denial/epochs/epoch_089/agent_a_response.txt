def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    resources = observation.get("resources", []) or []
    obstacles_list = observation.get("obstacles", []) or []
    obstacles = set()
    for p in obstacles_list:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obstacles.add((p[0], p[1]))

    def inb(x, y): return 0 <= x < w and 0 <= y < h
    def ok(x, y): return inb(x, y) and (x, y) not in obstacles
    def man(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx + dy

    moves = [(-1, 0), (1, 0), (0, -1), (0, 1), (-1, -1), (-1, 1), (1, -1), (1, 1), (0, 0)]
    if not resources:
        return [0, 0]

    best_move = (0, 0)
    best_score = -10**18

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not ok(nx, ny):
            continue

        my_d = 10**9
        opp_d = 10**9
        best_resource_gap = -10**18
        for r in resources:
            if not (isinstance(r, (list, tuple)) and len(r) >= 2):
                continue
            rx, ry = r[0], r[1]
            if not ok(rx, ry):
                continue
            d_self = man(nx, ny, rx, ry)
            d_opp = man(ox, oy, rx, ry)
            if d_self < my_d: my_d = d_self
            if d_opp < opp_d: opp_d = d_opp
            gap = d_opp - d_self  # positive if we are closer
            if gap > best_resource_gap:
                best_resource_gap = gap

        # Prefer moves that secure being closer to some resource, while minimizing distance.
        score = 0
        score += 2000 * best_resource_gap
        score -= 3 * my_d
        score += 0.5 * (opp_d - my_d)

        if score > best_score:
            best_score = score
            best_move = (dx, dy)

    return [best_move[0], best_move[1]]