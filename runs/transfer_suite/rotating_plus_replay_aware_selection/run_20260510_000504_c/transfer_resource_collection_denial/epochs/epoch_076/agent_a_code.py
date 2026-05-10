def choose_move(observation):
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)

    obstacles = set()
    for p in observation.get("obstacles", []) or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obstacles.add((int(p[0]), int(p[1])))
        elif isinstance(p, dict):
            q = p.get("position", None)
            if isinstance(q, (list, tuple)) and len(q) >= 2:
                obstacles.add((int(q[0]), int(q[1])))
            elif "x" in p and "y" in p:
                obstacles.add((int(p["x"]), int(p["y"])))

    resources = []
    for r in observation.get("resources", []) or []:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            resources.append((int(r[0]), int(r[1])))
        elif isinstance(r, dict):
            q = r.get("position", None)
            if isinstance(q, (list, tuple)) and len(q) >= 2:
                resources.append((int(q[0]), int(q[1])))
            elif "x" in r and "y" in r:
                resources.append((int(r["x"]), int(r["y"])))

    def cheb(a, b, c, d):
        da = abs(a - c); db = abs(b - d)
        return da if da > db else db

    # If standing on a resource, stay to secure it.
    for rx, ry in resources:
        if sx == rx and sy == ry:
            return [0, 0]

    # Choose best resource by tempo advantage (opponent arrival time minus ours).
    best = None
    best_score = -10**9
    for rx, ry in resources:
        if (rx, ry) in obstacles:
            continue
        ds = cheb(sx, sy, rx, ry)
        do = cheb(ox, oy, rx, ry)
        # Prefer positive tempo; break ties by closer to us and farther from opponent.
        score = (do - ds) * 10 - ds + (do // 2)
        if score > best_score:
            best_score = score
            best = (rx, ry)

    # Fallback: go toward nearest non-obstacle resource or stay.
    if best is None:
        for rx, ry in resources:
            if (rx, ry) not in obstacles:
                best = (rx, ry)
                break
    if best is None:
        return [0, 0]

    tx, ty = best

    # Pick move that is legal and best reduces distance; deterministic diagonal bias.
    moves = []
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles:
                moves.append((dx, dy, cheb(nx, ny, tx, ty)))
    if not moves:
        return [0, 0]
    # Sort: smallest remaining distance, then diagonal preference, then lexicographic.
    moves.sort(key=lambda m: (m[2], -abs(m[0]) - abs(m[1]), m[0], m[1]))
    return [int(moves[0][0]), int(moves[0][1])]