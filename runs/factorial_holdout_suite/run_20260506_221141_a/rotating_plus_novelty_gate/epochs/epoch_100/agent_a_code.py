def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0]) or [0, 0]
    ox, oy = observation.get("opponent_position", [w - 1, h - 1]) or [w - 1, h - 1]
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    blocked = set()
    for p in observation.get("obstacles", []) or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                blocked.add((x, y))

    resources = []
    for p in observation.get("resources", []) or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in blocked:
                resources.append((x, y))
    if not resources:
        return [0, 0]

    def kdist(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    # Choose target with best chance to arrive first; deterministic tie-break by coordinate.
    best = None
    for rx, ry in sorted(resources):
        sd = kdist(sx, sy, rx, ry)
        if sd == 0:
            return [0, 0]
        od = kdist(ox, oy, rx, ry)
        score = (od - sd, -sd, -rx, -ry)
        if best is None or score > best[0]:
            best = (score, rx, ry)
    _, tx, ty = best

    # Greedy one-step move toward target, avoiding obstacles/out of bounds; deterministic order.
    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best_m = (None, None)
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if nx < 0 or nx >= w or ny < 0 or ny >= h:
            continue
        if (nx, ny) in blocked:
            continue
        nd = kdist(nx, ny, tx, ty)
        # Slightly prefer moves that also reduce opponent distance (denial pressure).
        nod = kdist(ox, oy, tx, ty)
        opp_now = kdist(ox, oy, tx, ty)
        # Compare using arrival race margin after move.
        race_margin = opp_now - nd
        cand = (race_margin, -nd, -abs((nx - tx)) - abs((ny - ty)), dx, dy)
        if best_m[0] is None or cand > best_m[0]:
            best_m = (cand, (dx, dy))
    return [int(best_m[1][0]), int(best_m[1][1])]