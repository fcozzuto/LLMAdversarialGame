def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx = int(sx); sy = int(sy); ox = int(ox); oy = int(oy)

    obstacles = set()
    for p in (observation.get("obstacles") or []):
        if p and len(p) >= 2:
            x = int(p[0]); y = int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for r in (observation.get("resources") or []):
        if r and len(r) >= 2:
            x = int(r[0]); y = int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))
    if not resources:
        return [0, 0]

    def cheb(ax, ay, bx, by):
        dx = ax - bx; dy = ay - by
        if dx < 0: dx = -dx
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def cell_value(px, py):
        best = None
        for rx, ry in resources:
            sd = cheb(px, py, rx, ry)
            od = cheb(ox, oy, rx, ry)
            # Prefer cells that are close to a resource we can reach no later than opponent.
            # Also slightly prefer smaller self distance for tie-break.
            s = (sd - od, sd)
            if best is None or s < best[0]:
                best = (s, rx, ry)
        return best[0]

    cand = []
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx = sx + dx; ny = sy + dy
            if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles:
                cand.append((dx, dy))
    if not cand:
        return [0, 0]

    cand.sort(key=lambda m: (m[0], m[1]))
    best_move = cand[0]
    best = None
    for dx, dy in cand:
        nx = sx + dx; ny = sy + dy
        # One-step lookahead: favor moves that also don't let the opponent catch up immediately.
        score = cell_value(nx, ny)
        if best is None or score < best:
            best = score
            best_move = (dx, dy)
        elif score == best:
            # Deterministic: keep earlier in sorted order (already stable via cand sort).
            pass
    return [int(best_move[0]), int(best_move[1])]