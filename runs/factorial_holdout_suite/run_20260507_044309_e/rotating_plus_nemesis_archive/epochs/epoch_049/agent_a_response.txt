def choose_move(observation):
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))

    obstacles = set()
    for b in observation.get("obstacles") or []:
        if b and len(b) >= 2:
            bx, by = int(b[0]), int(b[1])
            if 0 <= bx < w and 0 <= by < h:
                obstacles.add((bx, by))

    resources = []
    for r in observation.get("resources") or []:
        if r and len(r) >= 2:
            rx, ry = int(r[0]), int(r[1])
            if 0 <= rx < w and 0 <= ry < h and (rx, ry) not in obstacles:
                resources.append((rx, ry))

    if not resources:
        return [0, 0]

    def man(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0:
            dx = -dx
        dy = y1 - y2
        if dy < 0:
            dy = -dy
        return dx + dy

    best = None
    for rx, ry in resources:
        ds = man(sx, sy, rx, ry)
        do = man(ox, oy, rx, ry)
        # Prefer resources we can beat/equal in time; then closer; then deterministic tie by position.
        key = (0 if ds <= do else 1, ds if ds <= do else -(do - ds), rx + ry, rx, ry)
        if best is None or key < best[0]:
            best = (key, rx, ry)

    _, tx, ty = best
    if sx == tx and sy == ty:
        return [0, 0]

    def sign(a):
        if a > 0:
            return 1
        if a < 0:
            return -1
        return 0

    candidates = []
    primary = (sign(tx - sx), sign(ty - sy))
    candidates.append(primary)

    dirs = [(-1, 0), (1, 0), (0, -1), (0, 1), (-1, -1), (-1, 1), (1, -1), (1, 1), (0, 0)]
    for d in dirs:
        if d not in candidates:
            candidates.append(d)

    best_move = (0, 0)
    best_dist = man(sx, sy, tx, ty) + 10
    best_block = True

    for dx, dy in candidates:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h):
            continue
        if (nx, ny) in obstacles:
            continue
        dist = man(nx, ny, tx, ty)
        if dist < best_dist or (dist == best_dist and (dx, dy) < best_move):
            best_dist = dist
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]