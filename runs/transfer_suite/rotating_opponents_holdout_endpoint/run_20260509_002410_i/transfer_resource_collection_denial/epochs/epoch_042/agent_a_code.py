def choose_move(observation):
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    obstacles = set()
    for p in observation.get("obstacles", []) or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if inb(x, y):
                obstacles.add((x, y))

    resources = []
    for p in observation.get("resources", []) or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if inb(x, y) and (x, y) not in obstacles:
                resources.append((x, y))
    if not resources:
        return [0, 0]

    def cheb(x1, y1, x2, y2):
        ax = x1 - x2
        if ax < 0:
            ax = -ax
        ay = y1 - y2
        if ay < 0:
            ay = -ay
        return ax if ax > ay else ay

    # Prefer resources where we are relatively closer than the opponent (race strategy),
    # and penalize targets that are far in absolute terms.
    best = None
    best_key = None
    for rx, ry in resources:
        myd = cheb(sx, sy, rx, ry)
        opd = cheb(ox, oy, rx, ry)
        # Strong race bias: if opponent is closer, heavily penalize.
        key = ((myd - opd), myd, rx + 31 * ry, opd)
        if best_key is None or key < best_key:
            best_key = key
            best = (rx, ry)

    tx, ty = best

    # Candidate moves: deterministic ordering (prefer diagonal, then x, then y).
    candidates = []
    for dx, dy in [(1, 1), (1, 0), (0, 1), (1, -1), (1, 0), (0, -1), (-1, 1), (-1, 0), (0, -1), (0, 0), (-1, -1), (-1, 0), (0, 1)]:
        nx, ny = sx + dx, sy + dy
        if dx in (-1, 0, 1) and dy in (-1, 0, 1) and inb(nx, ny) and (nx, ny) not in obstacles:
            candidates.append((dx, dy))
    if not candidates:
        return [0, 0]

    # If multiple resources are nearby, slightly bias toward moves that reduce "race margin"
    # while keeping path safe from immediate obstacle capture.
    def safe_score(dx, dy):
        nx, ny = sx + dx, sy + dy
        # Immediate safety: prefer avoiding stepping into cells adjacent to many obstacles.
        adj = 0
        for ax, ay in [(-1, 0), (1, 0), (0, -1), (0, 1), (-1, -1), (-1, 1), (1, -1), (1, 1)]:
            px, py = nx + ax, ny + ay
            if inb(px, py) and (px, py) in obstacles:
                adj += 1
        return -adj

    best_move = None
    best_move_key = None
    for dx, dy in candidates:
        nx, ny = sx + dx, sy + dy
        # Distance to target and race advantage after move.
        myd_next = cheb(nx, ny, tx, ty)
        opd_now = cheb(ox, oy, tx, ty)
        # Lower is better for (myd_next - opd_now); then reduce absolute myd_next.
        key = ((myd_next - opd_now), myd_next, safe_score(dx, dy), dx, dy)
        if best_move_key is None or key < best_move_key:
            best_move_key = key
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]