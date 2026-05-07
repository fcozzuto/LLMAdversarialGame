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
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx + dy

    def best_target():
        best = None
        for rx, ry in resources:
            ds = man(sx, sy, rx, ry)
            do = man(ox, oy, rx, ry)
            # Prefer resources we can reach no later than opponent; otherwise prefer biggest advantage.
            key = (0 if ds <= do else 1, ds if ds <= do else -(do - ds), rx + ry)
            if best is None or key < best[0]:
                best = (key, rx, ry)
        return best[1], best[2]

    tx, ty = best_target()
    if sx == tx and sy == ty:
        return [0, 0]

    moves = []
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            if dx == 0 and dy == 0:
                continue
            nx, ny = sx + dx, sy + dy
            if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles:
                moves.append((man(nx, ny, tx, ty), dx, dy))
    if not moves:
        return [0, 0]

    moves.sort(key=lambda t: (t[0], t[1], t[2]))
    return [int(moves[0][1]), int(moves[0][2])]