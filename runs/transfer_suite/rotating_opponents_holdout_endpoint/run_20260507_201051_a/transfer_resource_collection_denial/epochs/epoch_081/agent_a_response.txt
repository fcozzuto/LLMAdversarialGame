def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sx, sy = observation.get("self_position") or (0, 0)
    ox, oy = observation.get("opponent_position") or (w - 1, h - 1)
    sx = int(sx); sy = int(sy); ox = int(ox); oy = int(oy)

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

    if not resources:
        return [0, 0]

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def ok(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    deltas.sort(key=lambda d: (abs(d[0]) + abs(d[1]), d[0], d[1]))

    best_move = (0, 0)
    best_val = -10**18

    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not ok(nx, ny):
            nx, ny = sx, sy
        move_val = -10**18
        # Greedy-next state: pick the resource where we maximize (opp advantage) and minimize our distance.
        for i, (rx, ry) in enumerate(resources):
            sd = cheb(nx, ny, rx, ry)
            od = cheb(ox, oy, rx, ry)
            # Primary: we want to be closer than opponent (od - sd large).
            # Secondary: prefer capturing soon (smaller sd); tertiary: deterministic tie on index.
            val = (od - sd) * 1000 - sd * 5 - i
            if val > move_val:
                move_val = val
        # Small shaping: avoid moves that keep us from approaching selected best.
        if move_val > best_val:
            best_val = move_val
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]