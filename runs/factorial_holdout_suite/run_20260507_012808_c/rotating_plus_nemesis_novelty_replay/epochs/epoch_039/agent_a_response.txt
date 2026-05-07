def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    sx = int(sx); sy = int(sy); ox = int(ox); oy = int(oy)

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if p and len(p) >= 2:
            x = int(p[0]); y = int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for r in observation.get("resources") or []:
        if r and len(r) >= 2:
            x = int(r[0]); y = int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    def dist(x1, y1, x2, y2):
        dx = x1 - x2
        dy = y1 - y2
        if dx < 0: dx = -dx
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    if resources:
        best = None
        for rx, ry in resources:
            md = dist(sx, sy, rx, ry)
            od = dist(ox, oy, rx, ry)
            # Prefer resources we can reach sooner (large md/od advantage),
            # then prefer closer ones; slight bias to corner progression.
            corner_bias = 0.0
            if (rx == 0 or rx == w - 1) and (ry == 0 or ry == h - 1):
                corner_bias = 0.15
            score = (od - md) * 10.0 - md + corner_bias
            if best is None or score > best[0] or (score == best[0] and md < best[1]):
                best = (score, md, rx, ry)
        _, _, tx, ty = best
    else:
        # No visible resources: go to nearest non-obstacle corner deterministically.
        corners = [(0, 0), (0, h - 1), (w - 1, 0), (w - 1, h - 1)]
        best = None
        for cx, cy in corners:
            if (cx, cy) in obstacles:
                continue
            d = dist(sx, sy, cx, cy)
            if best is None or d < best[0]:
                best = (d, cx, cy)
        if best is None:
            return [0, 0]
        _, tx, ty = best

    # Choose a step that moves toward target while avoiding obstacles and opponent proximity.
    dxs = [-1, 0, 1]
    dys = [-1, 0, 1]
    candidates = []
    for dx in dxs:
        for dy in dys:
            if dx == 0 and dy == 0:
                continue
            nx = sx + dx
            ny = sy + dy
            if not (0 <= nx < w and 0 <= ny < h):
                continue
            if (nx, ny) in obstacles:
                continue
            if dist(nx, ny, tx, ty) > dist(sx, sy, tx, ty):
                continue
            opp_pen = dist(nx, ny, ox, oy)  # larger is better
            # Prefer reducing distance to target; break ties by staying farther from opponent.
            candidates.append((dist(nx, ny, tx, ty), -opp_pen, (dx, dy)))
    if not candidates:
        return [0, 0]
    candidates.sort()
    return [int(candidates[0][2][0]), int(candidates[0][2][1])]