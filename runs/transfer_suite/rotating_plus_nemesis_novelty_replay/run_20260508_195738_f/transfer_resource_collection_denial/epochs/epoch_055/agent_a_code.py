def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    obstacles = set((int(p[0]), int(p[1])) for p in (observation.get("obstacles", []) or []))
    resources = [(int(r[0]), int(r[1])) for r in (observation.get("resources", []) or [])]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best_move = (0, 0)
    best_val = -10**18

    if resources:
        # Pick a target we can reach strictly sooner than opponent (when possible), else least contested.
        # Deterministic tie-break by (advantage desc, self_dist asc, x asc, y asc).
        scored = []
        for rx, ry in resources:
            sd = cheb(sx, sy, rx, ry)
            od = cheb(ox, oy, rx, ry)
            adv = od - sd
            scored.append((adv, sd, rx, ry))
        scored.sort(key=lambda t: (-t[0], t[1], t[2], t[3]))
        # Use top candidate; if strongly contested, sample top few deterministically by evaluating immediate move.
        top = scored[:min(4, len(scored))]

        for dx, dy in deltas:
            nx, ny = sx + dx, sy + dy
            if not inb(nx, ny):
                continue
            val = -10**18
            # Immediate evaluation toward best of the selected top resources.
            for adv, sd, rx, ry in top:
                nsd = cheb(nx, ny, rx, ry)
                nod = cheb(ox, oy, rx, ry)
                # Prefer winning the next collection race; small bias to be closer.
                v = (nod - nsd) * 1000 - nsd
                # If we land on a resource, dominate.
                if (nx, ny) == (rx, ry):
                    v += 10**6
                if v > val:
                    val = v
            if val > best_val:
                best_val = val
                best_move = (dx, dy)
        return [int(best_move[0]), int(best_move[1])]

    # No resources: move toward the opponent-opposite corner (deterministic) while avoiding obstacles.
    corners = [(0, 0), (0, h - 1), (w - 1, 0), (w - 1, h - 1)]
    # choose corner farthest from opponent
    tc = corners[0]
    bestd = -1
    for c in corners:
        d = cheb(c[0], c[1], ox, oy)
        if d > bestd or (d == bestd and c < tc):
            bestd = d
            tc = c
    tx, ty = tc
    best = (0, 0)
    bestscore = -10**18
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        dist_to_corner = cheb(nx, ny, tx, ty)
        # Prefer minimizing distance to target corner
        score = -dist_to_corner
        if score > bestscore:
            bestscore = score
            best = (dx, dy)
    return [int(best[0]), int(best[1])]