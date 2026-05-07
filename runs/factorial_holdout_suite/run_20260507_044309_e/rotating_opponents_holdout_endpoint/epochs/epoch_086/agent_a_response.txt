def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for r in observation.get("resources") or []:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    if not resources:
        return [0, 0]

    candidates = []
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles:
                candidates.append((dx, dy))

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    best_move = (0, 0)
    best_val = -10**18
    for dx, dy in candidates:
        nx, ny = sx + dx, sy + dy
        val = 0
        immediate = 0
        # Evaluate by choosing the resource that maximizes "we arrive sooner"
        best_gap = -10**9
        best_self_dist = 10**9
        for tx, ty in resources:
            sd = cheb(nx, ny, tx, ty)
            od = cheb(ox, oy, tx, ty)
            if sd == 0:
                immediate = 1
            gap = od - sd  # positive => we are closer
            if gap > best_gap:
                best_gap = gap
            if sd < best_self_dist:
                best_self_dist = sd
        # Encourage grabbing now, otherwise win distance races; slight tie-break for closeness.
        val = (1000 if immediate else 0) + best_gap * 10 - best_self_dist
        if val > best_val:
            best_val = val
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]