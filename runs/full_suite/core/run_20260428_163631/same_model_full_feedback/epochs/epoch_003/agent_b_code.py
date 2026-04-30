def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", []) or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def safe(x, y):
        return inb(x, y) and (x, y) not in obstacles

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def clamp_inside(x, y):
        if x < 0: x = 0
        elif x >= w: x = w - 1
        if y < 0: y = 0
        elif y >= h: y = h - 1
        return x, y

    if not resources:
        dx = 0 if ox == sx else (1 if ox > sx else -1)
        dy = 0 if oy == sy else (1 if oy > sy else -1)
        nx, ny = sx + dx, sy + dy
        if safe(nx, ny):
            return [dx, dy]
        # obstacle-aware approach: pick best move that reduces distance to opponent
        best = [0, 0]
        bestv = -10**18
        for ddx, ddy in deltas:
            nx, ny = sx + ddx, sy + ddy
            if not safe(nx, ny):
                continue
            v = -cheb(nx, ny, ox, oy)
            if v > bestv:
                bestv = v
                best = [ddx, ddy]
        return best

    # Choose target resources that maximize relative progress; also try to push opponent away.
    # Use limited look: nearest few resources by current self distance.
    scored = []
    for rx, ry in resources:
        d = cheb(sx, sy, rx, ry)
        scored.append((d, rx, ry))
    scored.sort(key=lambda t: t[0])
    candidates = scored[:6] if len(scored) > 6 else scored

    best = [0, 0]
    bestv = -10**18
    for ddx, ddy in deltas:
        nx, ny = sx + ddx, sy + ddy
        if not safe(nx, ny):
            continue

        # Lower self distance is good; higher opponent distance is good.
        v = 0
        for _, rx, ry in candidates:
            self_d = cheb(nx, ny, rx, ry)
            opp_d = cheb(ox, oy, rx, ry)
            # Relative advantage weight; include direct progress.
            cur_self_d = cheb(sx, sy, rx, ry)
            v += (opp_d - self_d) * 3 + (cur_self_d - self_d) * 2

            # If move lands on a resource, strongly prioritize.
            if nx == rx and ny == ry:
                v += 10_000

        # Additional tie-breakers: avoid letting opponent get too close next turn to any candidate
        # by penalizing moves that decrease opponent advantage (relative).
        for _, rx, ry in candidates[:3]:
            cur_rel = (cheb(ox, oy, rx, ry) - cheb(sx, sy, rx, ry))
            new_rel = (cheb(ox, oy, rx, ry) - cheb(nx, ny, rx, ry))
            v += (new_rel - cur_rel)

        if v > bestv:
            bestv = v
            best = [ddx, ddy]

    # If best move is blocked by edge/clutter it won't be chosen due to safe(); still deterministic.
    # As a final guard, ensure output integers in {-1,0,1}.
    return [best[0], best[1]]