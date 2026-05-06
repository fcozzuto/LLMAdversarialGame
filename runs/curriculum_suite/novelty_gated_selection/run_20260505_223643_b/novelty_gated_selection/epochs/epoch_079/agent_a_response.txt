def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position", [0, 0]) or [0, 0]
    op = observation.get("opponent_position", [0, 0]) or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

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

    if not resources:
        return [0, 0]

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def best_dist2(x, y):
        dmin = None
        for rx, ry in resources:
            d = (rx - x) * (rx - x) + (ry - y) * (ry - y)
            if dmin is None or d < dmin:
                dmin = d
        return dmin if dmin is not None else 10**18

    def greedy_step(px, py):
        # assume opponent greedily minimizes squared distance to nearest remaining resource
        best = None
        best_move = (0, 0)
        for dx, dy in moves:
            nx, ny = px + dx, py + dy
            if not valid(nx, ny):
                nx, ny = px, py
            d2 = best_dist2(nx, ny)
            if best is None or d2 < best or (d2 == best and (dx, dy) < best_move):
                best, best_move = d2, (dx, dy)
        return px + best_move[0], py + best_move[1]

    best_score = None
    best_move = (0, 0)
    opp_next_base = None  # computed per our move since they can be affected only by resources; here resources fixed this turn

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            nx, ny = sx, sy

        # opponent response: greedy from their current position
        ox2, oy2 = greedy_step(ox, oy)

        d_self = best_dist2(nx, ny)
        d_opp = best_dist2(ox2, oy2)

        # maximize advantage; slight preference for reducing our distance when tied
        score = (d_opp - d_self, -d_self)
        if best_score is None or score > best_score or (score == best_score and (dx, dy) < best_move):
            best_score, best_move = score, (dx, dy)

    return [int(best_move[0]), int(best_move[1])]