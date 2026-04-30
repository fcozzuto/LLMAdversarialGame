def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    resources = observation.get("resources", []) or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))
    deltas = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def inb(x, y): return 0 <= x < w and 0 <= y < h
    def passable(x, y): return inb(x, y) and (x, y) not in obstacles

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    best_t = None
    best_v = -10**18
    if resources:
        for rx, ry in resources:
            ds = cheb(sx, sy, rx, ry)
            do = cheb(ox, oy, rx, ry)
            v = (do - ds) * 10 - ds  # prefer targets we are closer to
            if v > best_v:
                best_v = v
                best_t = (rx, ry)
    else:
        best_t = (w // 2, h // 2)

    rx, ry = best_t
    best_move = [0, 0]
    best_score = -10**18
    # Prefer moves that reduce our distance to the chosen target while increasing opponent distance.
    # Tie-break deterministically by lexicographic preference among deltas list order.
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not passable(nx, ny):
            continue
        ns = cheb(nx, ny, rx, ry)
        no = cheb(nx, ny, ox, oy)  # relative safety from opponent
        opp_to_target = cheb(ox, oy, rx, ry)
        # Encourage finishing if opponent is far; discourage if opponent can reach quickly.
        score = -ns * 5 + no * 0.2 + (opp_to_target - ns)
        if score > best_score:
            best_score = score
            best_move = [dx, dy]

    return best_move