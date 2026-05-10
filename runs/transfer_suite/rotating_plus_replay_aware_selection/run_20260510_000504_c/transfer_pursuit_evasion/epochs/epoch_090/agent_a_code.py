def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0]) or [0, 0]
    ox, oy = observation.get("opponent_position", [w - 1, h - 1]) or [w - 1, h - 1]
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = set()
    for p in observation.get("obstacles", []) or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    self_role = str(observation.get("self_role", "") or "").lower()
    opp_role = str(observation.get("opponent_role", "") or "").lower()
    is_pursuer = ("purs" in self_role) or ("chase" in self_role) or ("hunter" in self_role) or ("captur" in self_role)
    if not is_pursuer:
        is_pursuer = ("purs" in opp_role) == False  # default: if opponent looks like pursuer, self is evader

    deltas = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def dist2(x, y, a, b):
        dx, dy = x - a, y - b
        return dx * dx + dy * dy

    # Deterministic tie-break: fixed ordering of deltas, prefer smaller (dx,dy) lexicographically
    best = None
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        if (nx, ny) in obstacles:
            continue
        d2 = dist2(nx, ny, ox, oy)
        # Heuristic: approach with obstacle repulsion; evader: increase distance and avoid "dead" moves.
        if is_pursuer:
            # minimize distance, add penalty for moves that bring us adjacent to obstacles less? (avoid dead-ends by keeping options)
            adj_free = 0
            for ddx, ddy in deltas:
                tx, ty = nx + ddx, ny + ddy
                if inb(tx, ty) and (tx, ty) not in obstacles:
                    adj_free += 1
            val = -d2 + 0.12 * adj_free
        else:
            # maximize distance, and keep mobility
            adj_free = 0
            for ddx, ddy in deltas:
                tx, ty = nx + ddx, ny + ddy
                if inb(tx, ty) and (tx, ty) not in obstacles:
                    adj_free += 1
            val = d2 + 0.18 * adj_free
        key = (val, -dx, -dy)  # deterministic secondary ordering
        if best is None or key > best[0]:
            best = (key, (dx, dy))

    if best is None:
        # If surrounded by obstacles, stay still if valid
        if inb(sx, sy) and (sx, sy) not in obstacles:
            return [0, 0]
        for dx, dy in deltas:
            nx, ny = sx + dx, sy + dy
            if inb(nx, ny) and (nx, ny) not in obstacles:
                return [dx, dy]
        return [0, 0]
    return [best[1][0], best[1][1]]