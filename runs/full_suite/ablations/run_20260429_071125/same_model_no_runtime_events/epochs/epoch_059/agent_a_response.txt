def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sp = observation.get("self_position", [0, 0])
    op = observation.get("opponent_position", [w - 1, h - 1])
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

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    if not resources:
        for dx, dy in [(0, 0), (1, 0), (0, 1), (-1, 0), (0, -1), (1, 1), (1, -1), (-1, 1), (-1, -1)]:
            nx, ny = sx + dx, sy + dy
            if inb(nx, ny):
                return [dx, dy]
        return [0, 0]

    best_move = (0, 0)
    best_score = -10**18

    # Deterministic tie-break: prefer move ordering by (dx,dy) in moves list.
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue

        # Evaluate best target after this move; encourage taking resources we beat,
        # discourage chasing resources where opponent is already close/likely to arrive first.
        local_best = -10**18
        for tx, ty in resources:
            ds = cheb(nx, ny, tx, ty)
            do = cheb(ox, oy, tx, ty)

            # If opponent is closer, heavily penalize; if we are closer, reward.
            beat = do - ds  # positive means we are closer
            # Also add a small preference for nearer targets (faster pickup).
            pickup = -ds

            # Block tendency: if we could potentially grab before opponent,
            # prioritize that even if not the absolute closest resource.
            score = beat * 100 + pickup

            # Extra shaping: avoid targets adjacent to opponent where we might get contested.
            if cheb(ox, oy, tx, ty) <= 1 and ds > 1:
                score -= 80

            if score > local_best:
                local_best = score

        # Small preference to move towards the overall centroid of remaining resources.
        cx = 0
        cy = 0
        for tx, ty in resources:
            cx += tx
            cy += ty
        cx //= len(resources)
        cy //= len(resources)
        shaping = -cheb(nx, ny, cx, cy)
        total = local_best + shaping

        if total > best_score:
            best_score = total
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]