def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
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
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    # Pick resource where we are at least as close as opponent; otherwise deprioritize.
    best = None
    for rx, ry in resources:
        od = cheb(ox, oy, rx, ry)
        sd = cheb(sx, sy, rx, ry)
        key = (sd - od, sd, rx + ry)  # deterministic final tie
        if best is None or key < best[0]:
            best = (key, rx, ry)
    _, tx, ty = best

    # Choose move that best reduces distance to target; if we're behind, also drift toward opponent.
    behind = (cheb(sx, sy, tx, ty) - cheb(ox, oy, tx, ty)) > 0
    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    best_move = None
    best_key = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h): 
            continue
        if (nx, ny) in obstacles:
            continue
        d_to = cheb(nx, ny, tx, ty)
        d_opp = cheb(nx, ny, ox, oy)
        # Prefer grabbing progress; if behind, prioritize reducing opponent distance to contest space.
        key = (d_to, (d_opp if behind else -d_opp), (nx, ny))
        if best_key is None or key < best_key:
            best_key = key
            best_move = (dx, dy)

    if best_move is None:
        return [0, 0]
    return [int(best_move[0]), int(best_move[1])]