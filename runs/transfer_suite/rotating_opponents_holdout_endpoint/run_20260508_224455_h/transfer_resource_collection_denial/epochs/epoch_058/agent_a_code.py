def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    gw = int(observation["grid_width"])
    gh = int(observation["grid_height"])
    resources = observation.get("resources") or []
    obstacles = set((int(x), int(y)) for x, y in (observation.get("obstacles") or []))

    if not resources:
        return [0, 0]

    def inb(x, y):
        return 0 <= x < gw and 0 <= y < gh

    def valid(x, y):
        return inb(x, y) and (x, y) not in obstacles

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def obstacle_adj(x, y):
        c = 0
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                if dx == 0 and dy == 0:
                    continue
                if (x + dx, y + dy) in obstacles:
                    c += 1
        return c

    moves = []
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            if valid(nx, ny):
                moves.append((dx, dy, nx, ny))
    if not moves:
        return [0, 0]

    # Pick a resource we can contest: maximize (opp_dist - our_dist), tie-break by our_dist, then lexicographic.
    best = None
    for rx, ry in resources:
        rx, ry = int(rx), int(ry)
        our_d = cheb(sx, sy, rx, ry)
        opp_d = cheb(ox, oy, rx, ry)
        advantage = opp_d - our_d
        key = (-(advantage), our_d, rx, ry)  # minimized by advantage negative first; i.e., maximize advantage
        if best is None or key < best[0]:
            best = (key, (rx, ry), advantage, our_d, opp_d)

    _, (tx, ty), _, _, _ = best

    # Move one step toward target with collision-avoidance and deterministic tie-break.
    best_move = None
    for dx, dy, nx, ny in moves:
        # primary: reduce distance to target; secondary: avoid obstacle-adjacent; tertiary: deterministic lex on move
        d = cheb(nx, ny, tx, ty)
        adj = obstacle_adj(nx, ny)
        key = (d, adj, dx, dy)
        if best_move is None or key < best_move[0]:
            best_move = (key, [dx, dy])
    return best_move[1]