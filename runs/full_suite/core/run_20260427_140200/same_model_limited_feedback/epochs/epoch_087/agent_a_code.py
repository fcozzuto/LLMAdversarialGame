def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []
    occ = set((p[0], p[1]) for p in obstacles)

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def dsq(x1, y1, x2, y2):
        dx = x1 - x2
        dy = y1 - y2
        return dx * dx + dy * dy

    # Pick a deterministic best resource target
    target = None
    best_key = None
    for r in resources:
        tx, ty = r[0], r[1]
        key = (dsq(ox, oy, tx, ty) - dsq(sx, sy, tx, ty), dsq(sx, sy, tx, ty), tx, ty)
        if best_key is None or key < best_key:
            best_key = key
            target = (tx, ty)

    # Candidate moves: prefer smaller (dx,dy) by lexicographic order for determinism
    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    best_move = (0, 0)
    best_score = None

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in occ:
            continue
        if target is None:
            # Simple fallback: stay near own position, but avoid opponent vicinity
            score = (dsq(nx, ny, ox, oy), nx, ny)
        else:
            tx, ty = target
            score = (dsq(nx, ny, tx, ty), -dsq(nx, ny, ox, oy), nx, ny)
        if best_score is None or score < best_score:
            best_score = score
            best_move = [dx, dy]

    # If everything blocked, must stay put (validator expects always a legal return)
    nx, ny = sx, sy
    if not inb(nx, ny) or (nx, ny) in occ:
        # In unlikely case self position is invalid, clamp to a valid neighbor deterministically
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if inb(nx, ny) and (nx, ny) not in occ:
                return [dx, dy]
    return best_move