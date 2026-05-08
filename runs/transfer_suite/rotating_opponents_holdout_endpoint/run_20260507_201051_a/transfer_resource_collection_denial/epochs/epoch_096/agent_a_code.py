def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [w - 1, h - 1])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

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

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def best_target():
        if not resources:
            tx, ty = w // 2, h // 2
            return (tx, ty)
        best = None
        best_key = None
        for (rx, ry) in resources:
            dS = cheb(sx, sy, rx, ry)
            dO = cheb(ox, oy, rx, ry)
            # Higher means better: beat opponent on distance, also prefer nearer overall, then deterministic tie-break
            key = (dO - dS, - (dS + 2 * (abs(rx - w // 2) + abs(ry - h // 2)) / 999.0))
            if best_key is None or key > best_key or (key == best_key and (rx, ry) < best):
                best_key = key
                best = (rx, ry)
        return best

    tx, ty = best_target()

    # Choose move that reduces distance to chosen target, while avoiding obstacles/out-of-bounds
    best = None
    best_d = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h):
            continue
        if (nx, ny) in obstacles:
            continue
        d = cheb(nx, ny, tx, ty)
        key = (d, dx == 0 and dy == 0, dx, dy)
        if best is None or key < best:
            best = key
            best_d = (dx, dy)

    # If all moves invalid (surrounded), allow staying
    if best_d is None:
        return [0, 0]
    return [int(best_d[0]), int(best_d[1])]