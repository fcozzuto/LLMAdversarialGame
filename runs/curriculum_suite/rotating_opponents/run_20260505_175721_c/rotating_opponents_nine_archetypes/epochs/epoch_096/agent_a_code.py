def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", (0, 0)) or (0, 0)
    ox, oy = observation.get("opponent_position", (0, 0)) or (0, 0)
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

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0:
            dx = -dx
        dy = ay - by
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    def valid(nx, ny):
        return 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles

    # Choose a resource to maximize advantage over opponent; deny targets where opponent is ahead.
    best = None
    best_key = None
    for tx, ty in resources:
        dme = cheb(sx, sy, tx, ty)
        dome = cheb(ox, oy, tx, ty)
        # Prefer resources where we are closer; if opponent closer, still try to deny by moving toward them.
        advantage = dome - dme
        # Key: higher advantage first, then lower my distance, then deterministic tie-break on coordinates.
        key = (advantage, -dme, -tx, -ty)
        if best_key is None or key > best_key:
            best_key = key
            best = (tx, ty)

    tx, ty = best

    # Move one step toward target with obstacle-aware fallback.
    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best_step = (0, 0)
    best_dist = 10**9
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        d = cheb(nx, ny, tx, ty)
        if d < best_dist:
            best_dist = d
            best_step = (dx, dy)
        elif d == best_dist:
            # Deterministic tie-break: prefer steps that reduce cheb to target strictly in x then y ordering.
            if (dx, dy) < best_step:
                best_step = (dx, dy)

    return [int(best_step[0]), int(best_step[1])]