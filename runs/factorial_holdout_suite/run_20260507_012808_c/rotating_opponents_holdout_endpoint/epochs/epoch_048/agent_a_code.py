def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    sx = int(sx); sy = int(sy); ox = int(ox); oy = int(oy)

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if p and len(p) >= 2:
            x = int(p[0]); y = int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for r in observation.get("resources") or []:
        if r and len(r) >= 2:
            x = int(r[0]); y = int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))
    if not resources:
        return [0, 0]

    def dist_cheb(x1, y1, x2, y2):
        dx = abs(x1 - x2); dy = abs(y1 - y2)
        return dx if dx > dy else dy

    moves = []
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            moves.append((dx, dy))

    # Pick a target resource that we can reach earlier than opponent; break ties by closeness.
    best_target = resources[0]
    best_tscore = None
    for tx, ty in resources:
        myd = dist_cheb(sx, sy, tx, ty)
        opd = dist_cheb(ox, oy, tx, ty)
        # Prefer resources where opponent is slower, then nearer.
        tscore = (opd - myd) * 1000 - myd
        if best_tscore is None or tscore > best_tscore:
            best_tscore = tscore
            best_target = (tx, ty)

    tx, ty = best_target
    # Evaluate next moves: maximize improvement towards target while accounting for "denial" (being closer than opponent).
    best_move = (0, 0)
    best_val = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h) or (nx, ny) in obstacles:
            nx, ny = sx, sy
        myd2 = dist_cheb(nx, ny, tx, ty)
        opd = dist_cheb(ox, oy, tx, ty)
        # Also slightly prefer reducing distance to opponent (denier pressure) if tie.
        my_to_opp = dist_cheb(nx, ny, ox, oy)
        val = (opd - myd2) * 1000 - myd2 - my_to_opp * 0.01
        if best_val is None or val > best_val:
            best_val = val
            best_move = (dx if 1 >= dx >= -1 else 0, dy if 1 >= dy >= -1 else 0)

    return [int(best_move[0]), int(best_move[1])]