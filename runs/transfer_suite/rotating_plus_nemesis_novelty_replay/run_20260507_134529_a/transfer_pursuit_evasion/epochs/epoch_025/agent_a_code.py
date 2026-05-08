def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sx, sy = observation.get("self_position") or (0, 0)
    ox, oy = observation.get("opponent_position") or (0, 0)
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)
    obstacles = set()
    obs = observation.get("obstacles") or []
    for p in obs:
        if p is not None and len(p) >= 2:
            obstacles.add((int(p[0]), int(p[1])))

    resources = observation.get("resources") or []
    targets = []
    for r in resources:
        if r is None:
            continue
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            targets.append((int(r[0]), int(r[1])))
        elif isinstance(r, dict) and "position" in r:
            q = r["position"]
            if q is not None and len(q) >= 2:
                targets.append((int(q[0]), int(q[1])))

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def best_dist(x, y):
        if targets:
            md = 10**9
            for tx, ty in targets:
                d = (x - tx) * (x - tx) + (y - ty) * (y - ty)
                if d < md:
                    md = d
            return md
        return (x - ox) * (x - ox) + (y - oy) * (y - oy)

    best = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        val = best_dist(nx, ny)
        # Deterministic tie-breaker: prefer staying close to our current cell
        tie = abs(dx) + abs(dy)
        cand = (val, tie, dx, dy)
        if best is None or cand < best:
            best = cand

    if best is None:
        # If fully blocked, stay (if possible) else pick first valid neighbor
        if inb(sx, sy):
            return [0, 0]
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if inb(nx, ny):
                return [dx, dy]
    return [best[2], best[3]]