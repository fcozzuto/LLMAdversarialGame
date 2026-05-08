def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if inb(x, y):
                obstacles.add((x, y))

    resources = []
    for p in observation.get("resources") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if inb(x, y) and (x, y) not in obstacles:
                resources.append((x, y))
    if not resources:
        return [0, 0]

    def kingdist(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    # Choose resource where we are relatively closer than opponent; also bias away from their side.
    # Tie-break deterministically by coordinate.
    best = None
    best_score = None
    for rx, ry in resources:
        d_me = kingdist(sx, sy, rx, ry)
        d_op = kingdist(ox, oy, rx, ry)
        # Prefer resources we can reach no later than opponent; penalize those they can beat.
        # Small secondary bias to reduce travel and move towards our "own" quadrant (opposite corner).
        bias = ((sx - (w - 1 - ox)) * (rx - sx)) + ((sy - (h - 1 - oy)) * (ry - sy))
        score = (d_op - d_me) * 10 - d_me + (1 if bias > 0 else 0)
        key = (-(score), rx, ry)
        if best is None or key < best:
            best = key
            best_score = score

    _, tx, ty = best

    # Move toward target with obstacle-avoidance. If blocked, pick move that maximizes score after move.
    dirs = [(dx, dy) for dx in (-1, 0, 1) for dy in (-1, 0, 1)]
    candidates = []
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue
        d_me = kingdist(nx, ny, tx, ty)
        d_op = kingdist(ox, oy, tx, ty)
        # Encourage decreasing our distance; if tied, prefer those that improve relative advantage.
        rel = d_op - d_me
        candidates.append((-(rel * 10 - d_me), dx, dy, nx, ny))

    if not candidates:
        # Fallback: stay still rather than invalid moves
        return [0, 0]

    candidates.sort()
    return [int(candidates[0][1]), int(candidates[0][2])]