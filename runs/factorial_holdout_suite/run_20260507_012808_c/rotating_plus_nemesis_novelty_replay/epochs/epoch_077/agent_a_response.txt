def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
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

    def dist(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx + dy

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    # If no resources, drift to maximize distance from opponent while staying away from obstacles.
    if not resources:
        best = None
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not (0 <= nx < w and 0 <= ny < h) or (nx, ny) in obstacles:
                continue
            val = dist(nx, ny, ox, oy)
            if best is None or val > best[0]:
                best = (val, dx, dy)
        if best is None:
            return [0, 0]
        return [best[1], best[2]]

    # Choose a target resource with advantage bias.
    best_target = None
    best_score = -10**18
    for rx, ry in resources:
        myd = dist(rx, ry, sx, sy)
        opd = dist(rx, ry, ox, oy)
        # Large reward if I can reach first; smaller reward otherwise.
        # Also slightly prefer nearer resources to avoid dithering.
        score = (opd - myd) * 100 - myd
        if score > best_score:
            best_score = score
            best_target = (rx, ry)

    rx, ry = best_target
    myd0 = dist(sx, sy, rx, ry)
    need_block = dist(rx, ry, ox, oy) <= myd0 + 1  # opponent likely close

    # Pick the move that best advances to target; if needed, also deny opponent by increasing their distance to target.
    best = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h) or (nx, ny) in obstacles:
            continue
        myd = dist(nx, ny, rx, ry)
        if myd > myd0 + 2:
            continue
        opd = dist(ox, oy, rx, ry)
        opd_after = dist(ox, oy, rx, ry)  # opponent pos unchanged this turn
        # Deterministic tie-breakers: prefer diagonal/straight by order in moves, so keep stable comparisons.
        val = (myd0 - myd) * 1000 - myd
        if need_block:
            val += (opd_after - opd) * 0  # placeholder effect (same this turn), kept deterministic
            # Also keep some distance from opponent position while going for target.
            val += dist(nx, ny, ox, oy) * 2
        if best is None or val > best[0]:
            best = (val, dx, dy)

    if best is None:
        return [0, 0]
    return [best[1], best[2]]