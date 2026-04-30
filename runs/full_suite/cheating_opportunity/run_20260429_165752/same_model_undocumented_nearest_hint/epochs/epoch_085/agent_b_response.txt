def choose_move(observation):
    W = int(observation.get("grid_width") or 8)
    H = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [W - 1, H - 1]
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

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0:
            dx = -dx
        dy = ay - by
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    def inside(nx, ny):
        return 0 <= nx < W and 0 <= ny < H and (nx, ny) not in obstacles

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    # Choose a deterministic target: nearest resource, tie by lexicographic order.
    if resources:
        best_res = None
        best_d = None
        for (rx, ry) in resources:
            d = cheb(sx, sy, rx, ry)
            if best_res is None or d < best_d or (d == best_d and (rx, ry) < best_res):
                best_res, best_d = (rx, ry), d
        tx, ty = best_res
    else:
        # No visible resources: drift to increase distance from opponent and toward opposite corner.
        # Prefer moving away from opponent; tie-break toward (0,0) when opponent is closer to (7,7), else (7,7).
        far_corner = (0, 0) if cheb(ox, oy, 0, 0) <= cheb(ox, oy, W - 1, H - 1) else (W - 1, H - 1)
        tx, ty = far_corner

    # Score each move: closer to target is good; staying safe vs opponent is good; avoid getting into opponent's immediate reach.
    # Penalize proximity to opponent when opponent can match distance next step.
    opp_now = cheb(sx, sy, ox, oy)
    best_move = (0, 0)
    best_score = -10**18
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inside(nx, ny):
            continue
        d_t = cheb(nx, ny, tx, ty)
        d_o = cheb(nx, ny, ox, oy)

        # If we step onto a resource, that should dominate.
        onto_resource = 1 if resources and (nx, ny) == (tx, ty) else 0
        # Enemy "threat": how close opponent could be right after (assuming symmetric move ability).
        # Approx: if opponent is within 1 of us, strongly avoid.
        enemy_reach = 1 if cheb(ox, oy, nx, ny) <= 1 else 0

        # Deterministic tie-breaking via move ordering and lexicographic comparison on score.
        score = 0
        score += onto_resource * 10**6
        score += -10 * d_t
        score += 2 * (d_o - opp_now)
        score += -200000 * enemy_reach

        if score > best_score or (score == best_score and (dx, dy) < best_move):
            best_score = score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]