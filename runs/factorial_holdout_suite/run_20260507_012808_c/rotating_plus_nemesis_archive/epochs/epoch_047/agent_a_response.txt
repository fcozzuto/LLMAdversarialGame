def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w, h = int(observation["grid_width"]), int(observation["grid_height"])
    resources = observation.get("resources") or []
    obstacles = observation.get("obstacles") or []

    obs = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obs.add((x, y))

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    free = []
    for r in resources:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obs:
                free.append((x, y))

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obs

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    # Choose resource where we have the biggest (opponent_dist - self_dist) advantage; tie-break by smaller self distance.
    if free:
        best = None
        best_adv = None
        best_sd = None
        for tx, ty in free:
            sd = cheb(sx, sy, tx, ty)
            od = cheb(ox, oy, tx, ty)
            adv = od - sd
            if best is None or adv > best_adv or (adv == best_adv and (sd < best_sd or (sd == best_sd and (tx, ty) < best))):
                best = (tx, ty)
                best_adv = adv
                best_sd = sd
        tx, ty = best
        # Pick move that gets us closer, with obstacle-safe greedy; slight preference to reduce opponent distance too.
        bestm = (0, 0)
        bestscore = None
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not valid(nx, ny):
                continue
            sd2 = cheb(nx, ny, tx, ty)
            od2 = cheb(nx, ny, ox, oy)  # proxy: stay better positioned
            score = (sd2, od2, abs(dx) + abs(dy), nx, ny)
            if bestscore is None or score < bestscore:
                bestscore = score
                bestm = (dx, dy)
        return [bestm[0], bestm[1]]

    # No visible resources: move toward the open corner that is farthest from opponent (deterministic search-lite).
    corners = [(0, 0), (0, h - 1), (w - 1, 0), (w - 1, h - 1)]
    target = None
    bestd = None
    for cx, cy in corners:
        if valid(cx, cy):
            d = cheb(ox, oy, cx, cy)
            if target is None or d > bestd or (d == bestd and (cx, cy) < target):
                target = (cx, cy)
                bestd = d
    if target is None:
        return [0, 0]
    tx, ty = target

    bestm = (0, 0)
    bestscore = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        score = (cheb(nx, ny, tx, ty), cheb(nx, ny, ox, oy), nx, ny)
        if bestscore is None or score < bestscore:
            bestscore = score
            bestm = (dx, dy)
    return [bestm[0], bestm[1]]