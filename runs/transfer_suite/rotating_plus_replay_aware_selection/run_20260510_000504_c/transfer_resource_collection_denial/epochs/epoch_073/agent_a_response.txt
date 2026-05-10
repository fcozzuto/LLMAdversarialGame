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
        dx = abs(a - c); dy = abs(b - d)
        return dx if dx > dy else dy

    # Pick resource where we have a tempo advantage (earlier or tied, closer).
    best_t = None
    best_score = (10**9, 10**9)
    for rx, ry in resources:
        myd = cheb(sx, sy, rx, ry)
        opd = cheb(ox, oy, rx, ry)
        # Prefer advantage; then prefer shorter my distance; then prefer nearer to opponent (more likely contested).
        cand = (-1 if myd < opd else (0 if myd == opd else 1), myd, -opd)
        if best_t is None or cand < best_score:
            best_t = (rx, ry); best_score = cand

    tx, ty = best_t if best_t is not None else (sx, sy)
    if not resources:
        return [0, 0]

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best_move = (0, 0, 10**9)
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if nx < 0 or nx >= w or ny < 0 or ny >= h:
            continue
        if (nx, ny) in obstacles:
            continue
        dcur = cheb(nx, ny, tx, ty)
        # Small penalty if moving away from advantage against opponent target by keeping distance to opponent increasing.
        damp = cheb(nx, ny, tx, ty) - cheb(ox, oy, tx, ty)
        score = (dcur, damp, abs(nx - tx) + abs(ny - ty))
        if score < best_move[2:]:
            best_move = (dx, dy, score[0])
    return [int(best_move[0]), int(best_move[1])]