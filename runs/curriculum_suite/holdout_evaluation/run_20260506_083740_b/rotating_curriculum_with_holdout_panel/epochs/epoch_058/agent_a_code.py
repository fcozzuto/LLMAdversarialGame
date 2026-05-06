def choose_move(observation):
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []

    ob = set()
    for p in obstacles:
        if p and len(p) >= 2:
            ob.add((int(p[0]), int(p[1])))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def valid(x, y):
        return inb(x, y) and (x, y) not in ob

    def md(ax, ay, bx, by):
        return abs(ax - bx) + abs(ay - by)

    if not resources:
        return [0, 0]

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    # Choose a target that we can reach no worse than opponent; if none, pick nearest valid resource.
    best_targets = []
    for r in resources:
        if not r or len(r) < 2:
            continue
        rx, ry = int(r[0]), int(r[1])
        if not valid(rx, ry):
            continue
        d_me = md(sx, sy, rx, ry)
        d_opp = md(ox, oy, rx, ry)
        if d_me == 0:
            continue
        # Prefer resources where we are at least as close as opponent; otherwise deprioritize.
        if d_me <= d_opp:
            best_targets.append((d_opp - d_me, d_me, rx, ry))
    if best_targets:
        best_targets.sort()
        targets = [(t[2], t[3]) for t in best_targets[:4]]
    else:
        # Fallback: nearest valid resource (deterministic).
        vr = []
        for r in resources:
            if not r or len(r) < 2:
                continue
            rx, ry = int(r[0]), int(r[1])
            if valid(rx, ry):
                vr.append((md(sx, sy, rx, ry), rx, ry))
        vr.sort()
        targets = [(vr[0][1], vr[0][2])] if vr else [(sx, sy)]

    # Evaluate possible moves by how much they improve relative distance to chosen targets.
    best_move = [0, 0]
    best_score = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        # Larger is better.
        score = 0
        for tx, ty in targets:
            d_me = md(nx, ny, tx, ty)
            d_opp = md(ox, oy, tx, ty)
            # Gain for being closer than opponent; penalize allowing opponent to be closer.
            diff = d_opp - d_me
            score += (diff * 10) - d_me
            if diff >= 0:
                score += 50
        # Mild tie-break toward progressing away from center towards corners (match typical patrol patterns) and determinism.
        score += -md(nx, ny, w - 1, h - 1) if (sx + sy) < (ox + oy) else -md(nx, ny, 0, 0)
        if best_score is None or score > best_score or (score == best_score and (dx, dy) < tuple(best_move)):
            best_score = score
            best_move = [dx, dy]

    return best_move