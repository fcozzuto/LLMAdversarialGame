def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [w - 1, h - 1]
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

    def dist(a, b):
        dx = a[0] - b[0]
        if dx < 0: dx = -dx
        dy = a[1] - b[1]
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    if resources:
        rem = int(observation.get("remaining_resource_count") or len(resources))
        late = rem <= 5
        best = None
        best_key = None
        for r in resources:
            d1 = dist((sx, sy), r)
            d2 = dist((ox, oy), r)
            # Prefer resources we can reach earlier; go greedier late game.
            ahead = d2 - d1
            key = (0 if ahead > 0 else 1, -ahead if late else ahead, d1, r[0], r[1])
            if best_key is None or key < best_key:
                best_key = key
                best = r
        tx, ty = best
    else:
        tx, ty = ox, oy

    # Greedy step toward target while avoiding obstacles.
    cur = (sx, sy)
    best_step = (0, 0)
    best_val = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h):
            continue
        if (nx, ny) in obstacles:
            continue
        nd = dist((nx, ny), (tx, ty))
        # Tie-break deterministically: smaller distance, then lexicographic dx,dy.
        val = (nd, dx, dy)
        if best_val is None or val < best_val:
            best_val = val
            best_step = (dx, dy)

    return [best_step[0], best_step[1]]