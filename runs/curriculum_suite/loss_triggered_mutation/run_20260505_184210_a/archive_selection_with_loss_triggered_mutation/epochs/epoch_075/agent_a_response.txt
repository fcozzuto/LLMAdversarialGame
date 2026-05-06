def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = map(int, observation.get("self_position") or (0, 0))
    ox, oy = map(int, observation.get("opponent_position") or (w - 1, h - 1))

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

    def cd(a, b):
        ax, ay = a; bx, by = b
        dx = abs(ax - bx); dy = abs(ay - by)
        return dx if dx > dy else dy

    def best_resource():
        if not resources:
            return None
        me = (sx, sy)
        opp = (ox, oy)
        best = None
        best_key = None
        for r in resources:
            du = cd(me, r)
            do = cd(opp, r)
            # Prefer resources we can reach no later than opponent; otherwise, the ones where we're closest anyway.
            lateness = 0 if du <= do else (du - do)
            key = (lateness, du, r[0], r[1])  # deterministic tie-break
            if best is None or key < best_key:
                best = r
                best_key = key
        return best

    target = best_resource()
    if target is None:
        tx, ty = w // 2, h // 2
        target = (tx, ty)

    tx, ty = target
    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    best_move = (0, 0)
    best_val = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h):
            continue
        if (nx, ny) in obstacles:
            continue
        # Choose move that decreases our distance to target most; slight preference to also move away from opponent when tied.
        d = cd((nx, ny), (tx, ty))
        od = cd((nx, ny), (ox, oy))
        val = (d, -od, dx, dy)
        if best_val is None or val < best_val:
            best_val = val
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]