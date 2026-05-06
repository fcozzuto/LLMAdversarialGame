def choose_move(observation):
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    resources = observation.get("resources", []) or []
    obstacles = set((p[0], p[1]) for p in (observation.get("obstacles", []) or []))
    def inb(x, y): return 0 <= x < w and 0 <= y < h
    def valid(x, y): return inb(x, y) and (x, y) not in obstacles

    # If no resources, drift toward center-ish and away from opponent.
    if not resources:
        tx = 1 if sx > (w - 1) // 2 else (w - 2 if sx < (w - 1) // 2 else sx)
        ty = 1 if sy > (h - 1) // 2 else (h - 2 if sy < (h - 1) // 2 else sy)
        dx = 0
        if tx > sx: dx = 1
        elif tx < sx: dx = -1
        dy = 0
        if ty > sy: dy = 1
        elif ty < sy: dy = -1
        nx, ny = sx + dx, sy + dy
        if valid(nx, ny): return [dx, dy]
        # fallback
        for dx, dy in ((1,0),(-1,0),(0,1),(0,-1),(1,1),(1,-1),(-1,1),(-1,-1),(0,0)):
            if valid(sx+dx, sy+dy): return [dx, dy]
        return [0, 0]

    moves = [(-1, -1), (-1, 0), (-1, 1),
             (0, -1), (0, 0), (0, 1),
             (1, -1), (1, 0), (1, 1)]

    def man(a, b, c, d): return abs(a - c) + abs(b - d)

    best_score = -10**18
    best_move = [0, 0]
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny): 
            continue
        # Core: maximize "resource advantage" while also preferring closer cells.
        score = 0
        for rx, ry in resources:
            ds = man(nx, ny, rx, ry)
            do = man(ox, oy, rx, ry)
            # Big reward if we are closer; strong penalty if opponent is much closer.
            adv = do - ds
            score += 30 * (1 if adv > 0 else 0) + 8 * adv
            # Also reward reducing our distance.
            score += -2 * ds
        # Extra: prevent moving into dead areas by discouraging approaching obstacles tightly (local).
        # Penalize being adjacent to obstacles more than opponent is (simple density heuristic).
        for ax, ay in obstacles:
            if abs(nx - ax) <= 1 and abs(ny - ay) <= 1 and (ax, ay) != (nx, ny):
                score -= 1

        # If multiple moves tie, prefer the one that changes direction toward higher-value resources.
        if score > best_score:
            best_score = score
            best_move = [dx, dy]

    # Final safety: if somehow no valid move, stay.
    if valid(sx + best_move[0], sy + best_move[1]):
        return best_move
    for dx, dy in moves:
        if valid(sx+dx, sy+dy):
            return [dx, dy]
    return [0, 0]