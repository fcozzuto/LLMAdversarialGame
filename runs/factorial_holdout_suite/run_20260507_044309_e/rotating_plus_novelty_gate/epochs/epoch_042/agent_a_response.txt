def choose_move(observation):
    w = observation["grid_width"]; h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    obstacles = set(tuple(p) for p in (observation.get("obstacles") or []))
    dirs = [(-1,-1),(-1,0),(-1,1),(0,-1),(0,0),(0,1),(1,-1),(1,0),(1,1)]
    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles
    def man(x1, y1, x2, y2):
        dx = x1 - x2; dx = dx if dx >= 0 else -dx
        dy = y1 - y2; dy = dy if dy >= 0 else -dy
        return dx + dy
    resources = observation.get("resources") or []
    valid = []
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if inb(nx, ny):
            valid.append((dx, dy, nx, ny))
    if not valid:
        return [0, 0]
    if not resources:
        # deterministic: move toward opposite corner from opponent
        tx, ty = 0 if ox > w//2 else w-1, 0 if oy > h//2 else h-1
        best = None; best_key = None
        for dx, dy, nx, ny in valid:
            key = (man(nx, ny, tx, ty), dx, dy)
            if best_key is None or key < best_key:
                best_key = key; best = (dx, dy)
        return [best[0], best[1]]

    # score move by how strongly we are ahead on the next few resources
    # (higher = better). This differs from pure nearest-resource greediness.
    def move_score(nx, ny):
        scored = []
        for rx, ry in resources:
            myd = man(nx, ny, rx, ry)
            opd = man(ox, oy, rx, ry)
            # prefer resources we can reach earlier; strongly penalize resources opponent is much closer to
            ahead = opd - myd
            # slight preference for closer-than-opponent, tie-break by myd
            tie = 0.001 * myd
            scored.append((ahead - tie, myd, rx, ry))
        scored.sort(reverse=True)  # deterministic
        topk = scored[:3] if len(scored) >= 3 else scored
        # If we can capture immediately, prioritize it.
        cap_bonus = 0
        for ahead, myd, rx, ry in topk:
            if myd == 0:
                cap_bonus += 100
        # Also add a small anti-crowd term: avoid stepping toward opponent if it doesn't improve ahead.
        crowd = 0
        for ahead, myd, rx, ry in topk:
            if ahead < 0:
                crowd += (-ahead)
        total = cap_bonus + sum((a * 10 - m) for a, m, _, _ in topk) - 0.5 * crowd
        return total

    best_move = None; best_val = None
    for dx, dy, nx, ny in valid:
        v = move_score(nx, ny)
        key = (-v, dx, dy)  # deterministic on ties
        if best_val is None or key < best_val:
            best_val = key; best_move = (dx, dy)
    return [best_move[0], best_move[1]]