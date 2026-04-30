def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position", [0, 0]) or [0, 0]
    op = observation.get("opponent_position", [0, 0]) or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

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

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    deltas = [(-1,-1),(0,-1),(1,-1),(-1,0),(0,0),(1,0),(-1,1),(0,1),(1,1)]
    legal = [(dx, dy) for dx, dy in deltas if inb(sx + dx, sy + dy)]
    if not legal:
        return [0, 0]

    def dist(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    me = (sx, sy)
    opp = (ox, oy)

    # Pick a deterministic target: nearest, but prefer resources farther from opponent.
    if resources:
        tx, ty = min(resources, key=lambda r: (dist(me, r), -dist(opp, r), r[0], r[1]))
        target = (tx, ty)
    else:
        target = (w // 2, h // 2)

    best_move = (0, 0)
    best_score = None
    base_opp_d = dist(me, opp)

    for dx, dy in legal:
        nx, ny = sx + dx, sy + dy
        nd_me = (nx, ny)
        d_t = dist(nd_me, target)
        d_o = dist(nd_me, opp)

        # Encourage approaching target, keep away from opponent to avoid contention.
        # Also add a small tie-breaker to prefer increasing distance from opponent.
        score = (-d_t * 10) + (d_o - base_opp_d) * 2

        # If moving would land adjacent to opponent while target is not improved much, penalize.
        if abs(nx - ox) <= 1 and abs(ny - oy) <= 1:
            score -= 3 + (d_t > 0) * 1

        # Deterministic tie-break: prefer dx,dy ordering.
        if best_score is None or score > best_score or (score == best_score and (dx, dy) < best_move):
            best_score = score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]