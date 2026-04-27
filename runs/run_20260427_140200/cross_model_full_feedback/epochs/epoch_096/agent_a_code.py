def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    me = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    mx, my = int(me[0]), int(me[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in (observation.get("obstacles") or []):
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    resources = []
    for r in (observation.get("resources") or []):
        if r and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if inb(x, y) and (x, y) not in obstacles:
                resources.append((x, y))

    def manh(ax, ay, bx, by):
        return abs(ax - bx) + abs(ay - by)

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    if resources:
        target = min(resources, key=lambda t: (manh(mx, my, t[0], t[1]), t[0], t[1]))
        tx, ty = target
    else:
        tx, ty = (w // 2), (h // 2)

    best = None
    best_score = None
    for dx, dy in moves:
        nx, ny = mx + dx, my + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue
        myd = manh(nx, ny, tx, ty)
        opd = manh(ox, oy, tx, ty)
        # Prefer reducing distance to target; also prefer positions where we're not more behind than opponent.
        score = -myd + (myd <= opd) * 3 - (dx == 0 and dy == 0) * 0.1
        if best_score is None or score > best_score or (score == best_score and (dx, dy) < best):
            best_score = score
            best = (dx, dy)

    if best is None:
        for dx, dy in moves:
            nx, ny = mx + dx, my + dy
            if inb(nx, ny) and (nx, ny) not in obstacles:
                return [int(dx), int(dy)]
        return [0, 0]
    return [int(best[0]), int(best[1])]