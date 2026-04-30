def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [w - 1, h - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in (observation.get("obstacles") or []):
        if isinstance(p, (list, tuple)) and len(p) == 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for p in (observation.get("resources") or []):
        if isinstance(p, (list, tuple)) and len(p) == 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    def legal(nx, ny):
        return 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles

    if not resources:
        for dx, dy in [(1, 1), (1, 0), (0, 1), (0, 0), (-1, 0), (0, -1), (-1, -1), (1, -1), (-1, 1)]:
            nx, ny = sx + dx, sy + dy
            if legal(nx, ny):
                return [dx, dy]
        return [0, 0]

    best_move = (0, 0)
    best_score = -10**18

    # Pick a move that maximizes advantage to the best reachable resource.
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not legal(nx, ny):
            continue
        # Prefer reducing our distance; also prefer resources where we are closer than opponent.
        move_score = -10**18
        for rx, ry in resources:
            sd = cheb(nx, ny, rx, ry)
            od = cheb(ox, oy, rx, ry)
            # Big weight to winning claim; small tie-breaker toward nearer resources.
            adv = od - sd
            claim_bonus = 20 if sd <= od else 0
            score = adv * 10 + claim_bonus - 0.05 * sd
            if score > move_score:
                move_score = score

        # Secondary: if we can win multiple equally, push toward remaining resources by staying closer overall.
        if move_score > best_score:
            best_score = move_score
            best_move = (dx, dy)

    # Deterministic tie-break: if same score, prefer (0,0), then lexicographically smaller dx,dy.
    if best_move == (0, 0):
        return [0, 0]
    return [int(best_move[0]), int(best_move[1])]