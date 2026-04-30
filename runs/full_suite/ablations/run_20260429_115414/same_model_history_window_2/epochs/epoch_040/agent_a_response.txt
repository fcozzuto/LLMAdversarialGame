def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sx, sy = observation.get("self_position") or (0, 0)
    ox, oy = observation.get("opponent_position") or (0, 0)
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    blocked = set()
    for p in observation.get("obstacles") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                blocked.add((x, y))

    resources = []
    for r in observation.get("resources") or []:
        if r and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in blocked:
                resources.append((x, y))

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def ok(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in blocked

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    if not resources:
        # No visible resources: head toward opponent-weak region (toward opponent corner)
        tx, ty = (0, 7) if ox > w // 2 else (w - 1, 0)
        best = (0, 0)
        bestv = -10**18
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not ok(nx, ny): 
                continue
            v = -cheb(nx, ny, tx, ty)
            if v > bestv:
                bestv = v
                best = (dx, dy)
        return [best[0], best[1]]

    # Strategic change: compute best action by immediate "grab/deny" lead on the most promising resource.
    best = (0, 0)
    bestv = -10**18

    # Prefer earlier expansion / later racing: use turn_index as deterministic phase.
    t = int(observation.get("turn_index") or 0)
    lead_weight = 3.0 if t < 25 else 4.5
    race_weight = 0.9 if t < 25 else 1.6
    avoid_weight = 0.6

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not ok(nx, ny):
            continue

        # Immediate denial score: maximize over resources where we are closer than opponent.
        best_resource_v = -10**18
        for rx, ry in resources:
            sd = cheb(nx, ny, rx, ry)
            od = cheb(ox, oy, rx, ry)

            # Large value if we can reach much sooner (or at least keep lead).
            lead = od - sd  # positive means we are closer
            # Slight penalty for increasing our own distance to avoid dithering.
            v = lead_weight * lead - race_weight * sd

            # Tiny tie-break: resources closer to our current position than opponent's, favor consistency.
            if lead == 0:
                v -= 0.15 * sd

            if v > best_resource_v:
                best_resource_v = v

        # Obstacle proximity smoothing: prefer moves that are not "boxed in" (measured by local mobility).
        mobility = 0
        for mx, my in moves:
            px, py = nx + mx, ny + my
            if ok(px, py):
                mobility += 1
        v = best_resource_v + avoid_weight * mobility
        if v > bestv:
            bestv = v
            best = (dx, dy)

    return [best[0], best[1]]