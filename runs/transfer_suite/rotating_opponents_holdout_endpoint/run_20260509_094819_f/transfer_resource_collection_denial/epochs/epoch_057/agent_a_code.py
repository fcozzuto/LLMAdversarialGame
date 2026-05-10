def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    s = observation.get("self_position") or [0, 0]
    o = observation.get("opponent_position") or [0, 0]
    sx, sy = int(s[0]), int(s[1])
    ox, oy = int(o[0]), int(o[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for p in observation.get("resources") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    def cheb(a, b):
        dx = a[0] - b[0]
        dy = a[1] - b[1]
        if dx < 0: dx = -dx
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    moves = [(0,0),(1,0),(-1,0),(0,1),(0,-1),(1,1),(-1,-1),(1,-1),(-1,1)]
    if not resources:
        for dx, dy in [(1,1),(1,0),(0,1),(-1,0),(0,-1),(-1,-1),(1,-1),(-1,1),(0,0)]:
            nx, ny = sx + dx, sy + dy
            if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles:
                return [dx, dy]
        return [0, 0]

    # Prefer resources we can reach no later than opponent; if none, take the best "almost" target.
    best = None
    best_key = None
    for r in resources:
        sd = cheb((sx, sy), r)
        od = cheb((ox, oy), r)
        # primary: our lead (od - sd), then our distance, then deterministic coordinate tie-break
        lead = od - sd
        key = (lead, -sd, -r[0], -r[1])
        if best_key is None or key > best_key:
            best_key = key
            best = r

    tx, ty = best
    stepx = 0 if tx == sx else (1 if tx > sx else -1)
    stepy = 0 if ty == sy else (1 if ty > sy else -1)
    # Candidate steps biased toward target; avoid stepping into obstacles/bounds.
    candidates = [(stepx, stepy), (stepx, 0), (0, stepy), (stepx, -stepy), (-stepx, stepy), (-stepx, 0), (0, -stepy), (0,0)]
    def valid(dx, dy):
        nx, ny = sx + dx, sy + dy
        return 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles
    candidates = [(dx, dy) for dx, dy in candidates if valid(dx, dy)]
    if not candidates:
        for dx, dy in moves:
            if valid(dx, dy):
                candidates.append((dx, dy))
        if not candidates:
            return [0, 0]

    # Choose deterministically the step that maximizes eventual advantage to target (greedy lookahead).
    best_move = candidates[0]
    best_val = None
    for dx, dy in candidates:
        nx, ny = sx + dx, sy + dy
        sd = cheb((nx, ny), (tx, ty))
        od = cheb((ox, oy), (tx, ty))
        val = (od - sd, -sd, -nx, -ny)
        if best_val is None or val > best_val:
            best_val = val
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]