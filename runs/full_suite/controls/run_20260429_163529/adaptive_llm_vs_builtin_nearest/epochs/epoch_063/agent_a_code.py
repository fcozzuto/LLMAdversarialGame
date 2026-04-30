def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position", [0, 0]) or [0, 0]
    op = observation.get("opponent_position", [w - 1, h - 1]) or [w - 1, h - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles", []) or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for p in observation.get("resources", []) or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))
    if not resources:
        return [0, 0]

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    # Pick resource where we have the biggest distance advantage over opponent
    best = None
    best_score = None
    for rx, ry in resources:
        myd = cheb(sx, sy, rx, ry)
        opd = cheb(ox, oy, rx, ry)
        # favor big lead; if no lead, still prefer closer and more central
        lead = opd - myd
        center_bonus = -0.02 * (abs(rx - (w - 1) / 2.0) + abs(ry - (h - 1) / 2.0))
        score = lead - 0.01 * myd + center_bonus
        key = (score, lead, -myd, -rx, -ry)
        if best is None or key > best_score:
            best = (rx, ry)
            best_score = key

    tx, ty = best

    # Choose move that best progresses toward target while avoiding obstacles and opponent proximity
    deltas = [(-1,-1),(-1,0),(-1,1),(0,-1),(0,0),(0,1),(1,-1),(1,0),(1,1)]
    candidates = []
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h):
            continue
        if (nx, ny) in obstacles:
            continue
        d_to = cheb(nx, ny, tx, ty)
        d_from_opp = cheb(nx, ny, ox, oy)
        # primary: minimize distance to target; secondary: maximize distance from opponent
        cand_key = (-d_to, d_from_opp, -abs(nx - tx) - abs(ny - ty), -nx, -ny)
        candidates.append((cand_key, [dx, dy]))
    if not candidates:
        return [0, 0]

    candidates.sort(reverse=True)
    return candidates[0][1]