def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [w - 1, h - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for p in observation.get("resources") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def legal(nx, ny):
        return 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    # Deterministic tie-break: fixed move order

    if not resources:
        # Drift toward the corner opposite opponent (deterministic)
        tx = 0 if ox >= w // 2 else w - 1
        ty = 0 if oy >= h // 2 else h - 1
        best = (0, 0)
        bestv = -10**18
        for dxm, dym in moves:
            nx, ny = sx + dxm, sy + dym
            if not legal(nx, ny): 
                continue
            v = -(cheb(nx, ny, tx, ty)) + 0.05 * cheb(nx, ny, ox, oy)
            if v > bestv:
                bestv = v
                best = (dxm, dym)
        return [best[0], best[1]]

    # If multiple resources remain, target the nearest by current position.
    # Score moves to strongly prefer immediate resource capture, else progress + keep distance from opponent.
    best = (0, 0)
    bestv = -10**18
    for dxm, dym in moves:
        nx, ny = sx + dxm, sy + dym
        if not legal(nx, ny):
            continue

        # Resource capture is dominant
        if (nx, ny) in set(resources):
            return [dxm, dym]

        # Nearest-resource progress
        md_before = min(cheb(sx, sy, rx, ry) for (rx, ry) in resources)
        md_after = min(cheb(nx, ny, rx, ry) for (rx, ry) in resources)
        progress = md_before - md_after

        # Also bias away from opponent to avoid giving them tempo on the same resource
        opp_dist = cheb(nx, ny, ox, oy)

        # Deterministic small tie-break by closer to grid center
        cx, cy = w // 2, h // 2
        center_bias = -cheb(nx, ny, cx, cy) * 0.01

        v = 10.0 * progress + 0.05 * opp_dist + center_bias
        if v > bestv:
            bestv = v
            best = (dxm, dym)

    return [best[0], best[1]]