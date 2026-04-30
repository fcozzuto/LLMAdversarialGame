def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    me = observation.get("self_position", [0, 0]) or [0, 0]
    opp = observation.get("opponent_position", [0, 0]) or [0, 0]
    sx, sy = int(me[0]), int(me[1])
    ox, oy = int(opp[0]), int(opp[1])

    obstacles = set()
    for p in observation.get("obstacles", []) or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for r in observation.get("resources", []) or []:
        if r and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def cheb(a, b):
        dx = a[0] - b[0]
        if dx < 0: dx = -dx
        dy = a[1] - b[1]
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    if not resources:
        resources = [(sx, sy)]

    # Choose a target resource we can reach no later than the opponent (favor largest lead)
    my_scores = []
    for t in resources:
        tm = cheb((sx, sy), t)
        to = cheb((ox, oy), t)
        # "potential" prefers wins; also prefers earlier and closer when contested
        my_scores.append(((to - tm), -(tm + 0), -t[0] - 0.01 * t[1], t))
    my_scores.sort(reverse=True)
    _, _, _, target = my_scores[0]

    # Pick move: step toward target while keeping distance from opponent if contested
    best_move = (0, 0)
    best_val = -10**18

    # If we are behind on the chosen target, slightly prioritize survival/contesting adjacent squares
    tm_t = cheb((sx, sy), target)
    to_t = cheb((ox, oy), target)
    behind = (tm_t > to_t)

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        d_to = cheb((nx, ny), target)
        d_op = cheb((nx, ny), (ox, oy))
        lead_now = to_t - d_to  # positive means we are closer than opponent to target after move
        # Value components
        v = 0
        v += (1000 if not behind else 500) * lead_now
        v -= 3 * d_to
        v += (0 if resources else 0)
        v += (2 * d_op) if behind else (1 * d_op)  # when behind, staying farther helps avoid direct chase loss
        # Extra: avoid moving into opponent's likely reach next step by discouraging small d_op
        if d_op <= 1:
            v -= 30
        # Deterministic tie-break: lexicographic preference by (v, -d_op, -d_to, dx, dy)
        if v > best_val or (v == best_val and (-d_op, -d_to, dx, dy) > (-cheb((sx, sy), (ox, oy)), -cheb((sx, sy), target), best_move[0], best_move[1])):
            best_val = v
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]