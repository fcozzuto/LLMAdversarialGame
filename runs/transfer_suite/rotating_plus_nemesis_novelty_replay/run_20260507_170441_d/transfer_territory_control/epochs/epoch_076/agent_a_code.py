def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    blocked = set()
    obs = observation.get("obstacles") or []
    for p in obs:
        if p is None:
            continue
        try:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                blocked.add((x, y))
        except:
            pass

    unclaimed = observation.get("unclaimed_cells") or []
    candidates = [(0, 0), (1, 0), (-1, 0), (0, 1), (0, -1), (1, 1), (1, -1), (-1, 1), (-1, -1)]
    inb = lambda x, y: 0 <= x < w and 0 <= y < h

    def md(a, b, c, d):
        return abs(a - c) + abs(b - d)

    # Choose a deterministic target: far from opponent, not too far from self
    best = None
    best_val = -10**18
    if unclaimed:
        # Limit scan for brevity/determinism
        for i, cell in enumerate(unclaimed):
            if i > 80:
                break
            try:
                x, y = int(cell[0]), int(cell[1])
            except:
                continue
            if not inb(x, y) or (x, y) in blocked:
                continue
            val = md(ox, oy, x, y) - md(sx, sy, x, y)
            if val > best_val or (val == best_val and (x, y) < best):
                best_val = val
                best = (x, y)

    # If no target, just maximize distance from opponent while avoiding blocks
    if not best:
        best_move = (0, 0)
        best_score = -10**18
        for dx, dy in candidates:
            nx, ny = sx + dx, sy + dy
            if not inb(nx, ny) or (nx, ny) in blocked:
                continue
            score = md(ox, oy, nx, ny)
            if score > best_score or (score == best_score and (dx, dy) < best_move):
                best_score = score
                best_move = (dx, dy)
        return [int(best_move[0]), int(best_move[1])]

    tx, ty = best
    best_move = (0, 0)
    best_score = -10**18
    for dx, dy in candidates:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in blocked:
            continue
        # Prefer moving closer to target, while keeping/expanding advantage vs opponent
        score = -md(nx, ny, tx, ty) + 0.5 * md(nx, ny, ox, oy)
        if score > best_score or (score == best_score and (dx, dy) < best_move):
            best_score = score
            best_move = (dx, dy)
    return [int(best_move[0]), int(best_move[1])]