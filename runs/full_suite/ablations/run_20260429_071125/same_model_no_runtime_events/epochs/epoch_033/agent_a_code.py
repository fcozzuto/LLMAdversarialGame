def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
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
    for r in observation.get("resources") or []:
        if r and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    def king(a, b, c, d):
        dx = a - c
        if dx < 0: dx = -dx
        dy = b - d
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    best = (0, 0)
    best_val = -10**18

    # Choose best resource target by advantage, then move greedily to improve it.
    if resources:
        scored = []
        for rx, ry in resources:
            ds = king(sx, sy, rx, ry)
            do = king(ox, oy, rx, ry)
            # Prefer resources closer to us than opponent; tie-break by fewer total steps.
            scored.append((do - ds, -(ds + do), rx, ry))
        scored.sort(reverse=True)
        _, _, tx, ty = scored[0]
    else:
        tx, ty = w // 2, h // 2

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue

        # Main objective: reduce distance to target.
        ds_new = king(nx, ny, tx, ty)
        ds_old = king(sx, sy, tx, ty)
        progress = ds_old - ds_new

        # Secondary: maintain distance from opponent to reduce race losses.
        opp_dist = king(nx, ny, ox, oy)

        # Tertiary: if landing on/adjacent to any resource, slightly boost.
        near_resource = 0
        for rx, ry in resources:
            if king(nx, ny, rx, ry) == 0:
                near_resource = 6
                break
            if king(nx, ny, rx, ry) == 1:
                near_resource = max(near_resource, 2)

        val = progress * 100 + opp_dist * 3 + near_resource
        # Small deterministic tie-break: prefer moves that move generally toward center of board.
        cx, cy = w // 2, h // 2
        cen_old = king(sx, sy, cx, cy)
        cen_new = king(nx, ny, cx, cy)
        val += (cen_old - cen_new)

        if val > best_val:
            best_val = val
            best = (dx, dy)

    return [int(best[0]), int(best[1])]