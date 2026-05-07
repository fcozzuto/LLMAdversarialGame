def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    obstacles = set((p[0], p[1]) for p in (observation.get("obstacles", []) or []))
    resources = observation.get("resources", []) or []

    def ok(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    moves = []
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            if ok(nx, ny):
                moves.append((dx, dy, nx, ny))
    if not moves:
        return [0, 0]
    if not resources:
        tx, ty = (w - 1) // 2, (h - 1) // 2
        dx = 0 if sx == tx else (1 if sx < tx else -1)
        dy = 0 if sy == ty else (1 if sy < ty else -1)
        if ok(sx + dx, sy + dy):
            return [dx, dy]
        for dx, dy, _, _ in moves:
            if dx == dx and dy == dy:
                return [dx, dy]
        return [0, 0]

    def man(a, b, c, d):
        return abs(a - c) + abs(b - d)

    # Score each move by how much it improves our "race" advantage to the best resource.
    best_move = None
    best_score = None
    for dx, dy, nx, ny in moves:
        # Prefer making immediate progress to a resource that opponent is not closer to.
        local = -10**18
        for rx, ry in resources:
            ds = man(nx, ny, rx, ry)
            do = man(ox, oy, rx, ry)
            # Race advantage: lower self distance and higher opponent distance.
            # Tie-break: smaller sum to encourage faster collection.
            adv = (do - ds)
            fast = -(ds + do * 0.25)
            # If we step onto a resource, strongly prioritize it.
            take = 800 if (nx, ny) == (rx, ry) else 0
            local = max(local, take + adv * 20 + fast)
        # Small preference for staying off the opponent's direct path to prevent interception.
        gap_now = man(nx, ny, ox, oy)
        total = local + gap_now * 0.5
        if best_score is None or total > best_score or (total == best_score and (dx, dy) < (best_move[0], best_move[1])):
            best_score = total
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]