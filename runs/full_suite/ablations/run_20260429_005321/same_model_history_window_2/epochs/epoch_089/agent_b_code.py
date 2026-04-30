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
        if dx < 0:
            dx = -dx
        dy = y1 - y2
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    def legal(nx, ny):
        return 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    if resources:
        best = None
        best_key = None
        for tx, ty in resources:
            sd = cheb(sx, sy, tx, ty)
            od = cheb(ox, oy, tx, ty)
            # Primary: win the race to resource; Secondary: prefer closer; Tertiary: prefer lower "angular" stability
            key = (od - sd, -sd, -(tx + ty), -((tx - ty) if tx >= ty else (ty - tx)))
            if best_key is None or key > best_key:
                best_key = key
                best = (tx, ty)
        tx, ty = best
        target_dx = 0 if tx == sx else (1 if tx > sx else -1)
        target_dy = 0 if ty == sy else (1 if ty > sy else -1)
        candidates = []
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not legal(nx, ny):
                continue
            nd = cheb(nx, ny, tx, ty)
            # Prefer reducing distance to target; tie-break by matching greedy direction
            greedy_match = -(abs(dx - target_dx) + abs(dy - target_dy))
            candidates.append((-(nd), greedy_match, dx, dy))
        candidates.sort()
        return [int(candidates[0][2]), int(candidates[0][3])] if candidates else [0, 0]

    # No resources: move to a deterministic "safe" corner opposite opponent, avoiding obstacles if needed.
    desired = (0, 0)
    if ox >= w // 2:
        desired = (w - 1, 0)
    else:
        desired = (0, h - 1)
    tx, ty = desired
    best = None
    best_key = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not legal(nx, ny):
            continue
        # Prefer maximizing distance from opponent while going toward desired corner
        key = (cheb(nx, ny, ox, oy), -cheb(nx, ny, tx, ty), -(dx * dx + dy * dy))
        if best_key is None or key > best_key:
            best_key = key
            best = (dx, dy)
    return [int(best[0]), int(best[1])] if best is not None else [0, 0]