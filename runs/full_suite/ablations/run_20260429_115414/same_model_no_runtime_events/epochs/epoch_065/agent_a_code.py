def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position", [0, 0]) or [0, 0]
    op = observation.get("opponent_position", [w - 1, h - 1]) or [w - 1, h - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for p in observation.get("resources") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0:
            dx = -dx
        dy = ay - by
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    if resources:
        best = None
        best_score = -10**9
        for rx, ry in resources:
            ds = cheb(sx, sy, rx, ry)
            do = cheb(ox, oy, rx, ry)
            # Prefer targets we can reach first; lightly penalize being far.
            score = (do - ds) * 10 - ds
            if score > best_score:
                best_score = score
                best = (rx, ry)
        tx, ty = best
        # Move to reduce our distance, with deterministic tie-breaking.
        curr_d = cheb(sx, sy, tx, ty)
        curr_od = cheb(ox, oy, sx, sy)
        chosen = (0, 0)
        chosen_key = None
        for dx, dy in deltas:
            nx, ny = sx + dx, sy + dy
            if not valid(nx, ny):
                continue
            d = cheb(nx, ny, tx, ty)
            # Keep from walking into the opponent if equally good.
            od = cheb(nx, ny, ox, oy)
            key = (-(d), (od), -(abs(nx - tx) + abs(ny - ty)), -((dx != 0 and dy != 0) is True), -((dx == 0) and (dy == 0)))
            if chosen_key is None or key > chosen_key or (key == chosen_key and (dx, dy) < chosen):
                chosen_key = key
                chosen = (dx, dy)
        return [int(chosen[0]), int(chosen[1])]
    else:
        # No visible resources: drift toward center while keeping distance from opponent.
        cx, cy = (w - 1) // 2, (h - 1) // 2
        chosen = (0, 0)
        chosen_key = None
        for dx, dy in deltas:
            nx, ny = sx + dx, sy + dy
            if not valid(nx, ny):
                continue
            dc = cheb(nx, ny, cx, cy)
            od = cheb(nx, ny, ox, oy)
            key = (-(dc), od, -((dx != 0 and dy != 0) is True), (dx, dy) < chosen)
            if chosen_key is None or key > chosen_key:
                chosen_key = key
                chosen = (dx, dy)
        return [int(chosen[0]), int(chosen[1])]