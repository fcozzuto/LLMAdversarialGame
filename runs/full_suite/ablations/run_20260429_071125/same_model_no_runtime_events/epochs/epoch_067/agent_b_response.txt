def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [w - 1, h - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in (observation.get("obstacles") or []):
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for r in (observation.get("resources") or []):
        if r and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))
    if not resources:
        return [0, 0]

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def safe_penalty(x, y):
        # small penalty if adjacent to obstacles to avoid being funneled
        pen = 0
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                nx, ny = x + dx, y + dy
                if (nx, ny) in obstacles:
                    pen += 1
        return pen

    dirs = [(-1, -1), (0, -1), (1, -1),
            (-1, 0), (0, 0), (1, 0),
            (-1, 1), (0, 1), (1, 1)]
    dirs.sort()  # deterministic tie-break

    best_move = (0, 0)
    best_score = None

    # Evaluate each candidate move by the best resource after the move,
    # but also discourage moves that let the opponent get a large advantage.
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        # If the move is identical, still consider.
        move_score = None
        for tx, ty in resources:
            ds = cheb(nx, ny, tx, ty)
            do = cheb(ox, oy, tx, ty)
            # Favor resources we can beat; penalize those the opponent is closer to.
            # Tie-break uses coords to keep deterministic.
            beat = do - ds  # positive = we are closer
            coord_bias = -0.001 * (abs(tx - (w - 1)) + abs(ty - (h - 1)))
            candidate = 10.0 * beat - 0.35 * ds - 0.75 * max(0, ds - do) + coord_bias
            if move_score is None or candidate > move_score:
                move_score = candidate
        # Add safety: discourage stepping near obstacles
        move_score -= 0.12 * safe_penalty(nx, ny)
        if best_score is None or move_score > best_score:
            best_score = move_score
            best_move = (dx, dy)

    dx, dy = best_move
    if dx not in (-1, 0, 1) or dy not in (-1, 0, 1):
        return [0, 0]
    return [int(dx), int(dy)]