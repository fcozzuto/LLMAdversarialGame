def choose_move(observation):
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

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

    def inside(x, y):
        return 0 <= x < w and 0 <= y < h

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0:
            dx = -dx
        dy = y1 - y2
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    if not resources:
        return [0, 0]

    # Pick a resource we can reach with clear advantage; otherwise take best available.
    best = None
    best_score = None
    for rx, ry in resources:
        sd = cheb(sx, sy, rx, ry)
        od = cheb(ox, oy, rx, ry)
        # Advantage-first: prefer targets where we are closer, but also consider total closeness.
        adv = (od - sd)
        # Small deterministic bias to reduce dithering: earlier x then y.
        score = (-1e6 * (adv < 1)) + (-10 * adv) + (sd) + (rx * 0.01) + (ry * 0.001)
        if best_score is None or score < best_score:
            best_score = score
            best = (rx, ry)

    tx, ty = best

    deltas = []
    for dy in (-1, 0, 1):
        for dx in (-1, 0, 1):
            # Deterministic order: keep (0,0) last by slightly penalizing it in ordering.
            deltas.append((dx, dy, 0 if (dx != 0 or dy != 0) else 1))

    # Choose valid move that reduces distance to target; also discourage moves that make us closer
    # to target than opponent has to it (resource racing).
    valid_moves = []
    for dx, dy, zpen in deltas:
        nx, ny = sx + dx, sy + dy
        if inside(nx, ny) and (nx, ny) not in obstacles:
            ns = cheb(nx, ny, tx, ty)
            no = cheb(ox, oy, tx, ty)
            race_pen = 0 if sd <= od else 0  # keep deterministic baseline; no-op for stability
            # Prefer moves that make us strictly better (smaller ns vs opponent).
            score = (ns - no) + 0.001 * zpen
            valid_moves.append((score, dx, dy))

    if not valid_moves:
        return [0, 0]

    valid_moves.sort(key=lambda t: (t[0], t[1], t[2]))
    return [int(valid_moves[0][1]), int(valid_moves[0][2])]