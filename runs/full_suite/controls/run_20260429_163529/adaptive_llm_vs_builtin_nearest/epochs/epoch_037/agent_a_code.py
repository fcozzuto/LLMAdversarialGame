def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position", [0, 0]) or [0, 0]
    op = observation.get("opponent_position", [w - 1, h - 1]) or [w - 1, h - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []
    obs = set()
    for p in obstacles:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obs.add((x, y))

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0:
            dx = -dx
        dy = ay - by
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    if not resources:
        return [0, 0]

    # Prefer resources we can reach no later than opponent; otherwise steal "least-winnable" by opponent.
    cx, cy = (w - 1) / 2.0, (h - 1) / 2.0
    best = None
    best_key = None
    for p in resources:
        if not p or len(p) < 2:
            continue
        rx, ry = int(p[0]), int(p[1])
        if (rx, ry) in obs:
            continue
        d_me = cheb(sx, sy, rx, ry)
        d_op = cheb(ox, oy, rx, ry)
        # large weight to race outcome; small tie-breaks for centrality and urgency
        race = d_op - d_me
        central = -(abs(rx - cx) + abs(ry - cy)) * 0.01
        urgency = -d_me * 0.02
        steal_bonus = 0.35 if d_me <= d_op else 0.0
        key = (race + central + urgency + steal_bonus, -d_me, -abs(rx - ox) - abs(ry - oy))
        if best_key is None or key > best_key:
            best_key = key
            best = (rx, ry)

    if best is None:
        return [0, 0]
    tx, ty = best

    moves = [(dx, dy) for dx in (-1, 0, 1) for dy in (-1, 0, 1)]
    # deterministic order: prefer moves that reduce distance, avoid obstacles, then prefer diagonal/forward for stability
    bestm = None
    bestscore = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h) or (nx, ny) in obs:
            continue
        d = cheb(nx, ny, tx, ty)
        # obstacle-denial: if opponent is close to the chosen target, reduce our distance more aggressively
        opp_d = cheb(ox, oy, tx, ty)
        aggress = 0.0 if opp_d > d_me else 0.25  # uses last computed d_me? might be undefined if best loop skipped; safe fallback:
        try:
            aggress = 0.25 if cheb(ox, oy, tx, ty) <= cheb(sx, sy, tx, ty) else 0.0
        except:
            aggress = 0.0
        # stable preference: avoid oscillation by lightly penalizing moves that increase distance to current position's best estimate
        score = (-d) + aggress * (-d) + (-0.001 * (abs(dx) + abs(dy))) + (0.0001 * (dx * dy))
        if bestscore is None or score > bestscore:
            bestscore = score
            bestm = (dx, dy)

    if bestm is None:
        return [0, 0]
    return [int(bestm[0]), int(bestm[1])]