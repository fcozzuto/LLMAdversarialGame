def choose_move(observation):
    W = int(observation.get("grid_width") or 8)
    H = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [W - 1, H - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < W and 0 <= y < H:
                obstacles.add((x, y))

    resources = []
    for p in observation.get("resources") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < W and 0 <= y < H and (x, y) not in obstacles:
                resources.append((x, y))

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def valid(nx, ny):
        return 0 <= nx < W and 0 <= ny < H and (nx, ny) not in obstacles

    def dist(a, b, c, d):
        dx = a - c
        if dx < 0: dx = -dx
        dy = b - d
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def choose_target():
        if not resources:
            return (W // 2, H // 2)
        best = None
        best_key = None
        for rx, ry in resources:
            md = dist(sx, sy, rx, ry)
            od = dist(ox, oy, rx, ry)
            # Prefer resources we can reach no later than opponent; then closest to us.
            if md <= od:
                key = (0, md, rx, ry)
            else:
                # Otherwise, pick where we fall behind the least; then closest to us.
                key = (1, od - md, md, rx, ry)
            if best_key is None or key < best_key:
                best_key = key
                best = (rx, ry)
        return best

    tx, ty = choose_target()

    best_move = (0, 0)
    best_key = None
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        d1 = dist(nx, ny, tx, ty)
        # Deterministic tie-break: fewer obstacles-avoidance not needed; stable by coordinates.
        key = (d1, abs(dx) + abs(dy), dx, dy)
        if best_key is None or key < best_key:
            best_key = key
            best_move = (dx, dy)

    if valid(sx + best_move[0], sy + best_move[1]):
        return [int(best_move[0]), int(best_move[1])]

    for dx, dy in deltas:
        if valid(sx + dx, sy + dy):
            return [int(dx), int(dy)]
    return [0, 0]