def choose_move(observation):
    W = int(observation.get("grid_width", 8))
    H = int(observation.get("grid_height", 8))
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = observation.get("obstacles") or []
    obs = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < W and 0 <= y < H:
                obs.add((x, y))

    resources = observation.get("resources") or []
    res = []
    for p in resources:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < W and 0 <= y < H and (x, y) not in obs:
                res.append((x, y))

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def legal(nx, ny):
        return 0 <= nx < W and 0 <= ny < H and (nx, ny) not in obs

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    best = (0, 0)
    best_score = -10**18

    # If no resources, move to maximize distance from opponent (prefer far corner).
    if not res:
        corners = [(0, 0), (0, H - 1), (W - 1, 0), (W - 1, H - 1)]
        tc = corners[0]
        td = cheb(ox, oy, tc[0], tc[1])
        for c in corners[1:]:
            d = cheb(ox, oy, c[0], c[1])
            if d < td:
                td = d
                tc = c
        targetx, targety = tc[0], tc[1]
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not legal(nx, ny):
                continue
            s = cheb(nx, ny, targetx, targety)
            if s > best_score:
                best_score = s
                best = (dx, dy)
        return [best[0], best[1]]

    # Resource-seeking with deterministic competition pressure.
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not legal(nx, ny):
            continue
        score = 0
        min_self = 10**9
        min_opp = 10**9
        for rx, ry in res:
            ds = cheb(nx, ny, rx, ry)
            do = cheb(ox, oy, rx, ry)
            if (rx == nx and ry == ny):
                score += 1000  # immediate pick priority
            # Favor resources where we can beat the opponent.
            score += (do - ds) * 8
            # Also prefer closer resources regardless, but less strongly.
            score += (20 - ds) * 1
            if ds < min_self: min_self = ds
            if do < min_opp: min_opp = do
        # Slight tie-break: prefer reducing our distance to the nearest resource.
        score += (min_opp - min_self) * 2
        # Small penalty for moving near obstacles (deterministic local safety).
        for oxp, oyp in obs:
            if cheb(nx, ny, oxp, oyp) == 1:
                score -= 3
        if score > best_score:
            best_score = score
            best = (dx, dy)
    return [best[0], best[1]]