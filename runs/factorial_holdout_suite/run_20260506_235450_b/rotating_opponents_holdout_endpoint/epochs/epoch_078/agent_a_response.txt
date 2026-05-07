def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position", [0, 0]) or [0, 0]
    ap = observation.get("opponent_position", [w - 1, h - 1]) or [w - 1, h - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(ap[0]), int(ap[1])

    obstacles = set()
    for o in observation.get("obstacles", []) or []:
        if isinstance(o, (list, tuple)) and len(o) >= 2:
            x, y = int(o[0]), int(o[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for r in observation.get("resources", []) or []:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))
    if not resources:
        return [0, 0]

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0:
            dx = -dx
        dy = y1 - y2
        if dy < 0:
            dy = -dy
        return dx if dx >= dy else dy

    tr = int(observation.get("remaining_resource_count", 999) or 999)
    endgame = tr <= 5

    # Prefer: (a) resources we can reach no later than opponent, (b) closer total,
    # (c) avoid those "behind" obstacles relative to both (simple directional penalty).
    best = None
    best_score = None
    for x, y in resources:
        sd = cheb(sx, sy, x, y)
        od = cheb(ox, oy, x, y)

        # Simple obstacle risk: count obstacles in the bounding box along a diagonal-ish corridor.
        # (No pathfinding; just deterministic local penalty.)
        minx = x if x < sx else sx
        maxx = x if x > sx else sx
        miny = y if y < sy else sy
        maxy = y if y > sy else sy
        risk_s = 0
        if maxx - minx <= 3 and maxy - miny <= 3:
            for (bx, by) in obstacles:
                if minx <= bx <= maxx and miny <= by <= maxy:
                    risk_s += 1

        minx2 = x if x < ox else ox
        maxx2 = x if x > ox else ox
        miny2 = y if y < oy else oy
        maxy2 = y if y > oy else oy
        risk_o = 0
        if maxx2 - minx2 <= 3 and maxy2 - miny2 <= 3:
            for (bx, by) in obstacles:
                if minx2 <= bx <= maxx2 and miny2 <= by <= maxy2:
                    risk_o += 1

        reach_adv = od - sd  # positive means we are faster
        # Score: in midgame heavily deny; in endgame prioritize our quickest.
        if endgame:
            score = (0.0 - sd) - 0.35 * risk_s + 0.10 * (reach_adv)
        else:
            score = (3.0 * reach_adv) - (0.2 * sd) - (1.1 * risk_o) - 0.35 * risk_s

        # Tie-break deterministically by lexicographic (x,y).
        key = (score, -x, -y)
        if best is None or key > best_score:
            best = (x, y)
            best_score = key

    tx, ty = best
    dx = 0 if tx == sx else (1 if tx > sx else -1)
    dy = 0 if ty == sy else (1 if ty > sy else -1)

    # If target is occupied by obstacle (shouldn't happen), step to safer alternative: toward opponent or stay.
    if (tx, ty) in obstacles:
        return [0, 0]
    return [dx, dy]