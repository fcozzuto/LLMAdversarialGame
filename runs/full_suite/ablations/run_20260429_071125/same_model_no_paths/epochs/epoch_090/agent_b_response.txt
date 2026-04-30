def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for r in observation.get("resources") or []:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    moves = []
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            if valid(nx, ny):
                moves.append((dx, dy, nx, ny))

    if not moves:
        return [0, 0]
    if not resources:
        return [0, 0]

    # Precompute a deterministic tie-break ordering for targets
    resources_sorted = sorted(resources, key=lambda p: (p[0], p[1]))

    best_move = None
    best_score = None

    # New strategy: one-step lookahead, choose move maximizing advantage on the best obtainable target.
    for dx, dy, nx, ny in moves:
        # For each possible position, choose the single target that gives us best relative progress.
        best_adv = None
        best_tie = None
        for rx, ry in resources_sorted:
            ds = cheb(nx, ny, rx, ry)
            do = cheb(ox, oy, rx, ry)
            # Advantage: higher means opponent farther than we are
            adv = do - ds
            # Slight preference for nearer targets once advantage is tied
            tie = (adv, -do, -ds, rx, ry)
            if best_adv is None or tie > best_tie:
                best_adv = adv
                best_tie = tie

        # If we can capture a resource immediately, prioritize strongly.
        immediate = 1 if any((nx, ny) == t for t in resources) else 0

        # Also prevent walking away from where we already are in relation to opponent.
        center_adv_now = cheb(ox, oy, nx, ny)  # distance between agents after move
        score = (immediate, best_adv, -center_adv_now, dx, dy)

        if best_score is None or score > best_score:
            best_score = score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]