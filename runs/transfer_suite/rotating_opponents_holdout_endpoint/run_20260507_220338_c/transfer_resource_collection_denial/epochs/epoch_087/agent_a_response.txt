def choose_move(observation):
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))

    obst = set()
    for p in observation.get("obstacles", []) or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obst.add((x, y))

    resources = []
    for p in observation.get("resources", []) or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obst:
                resources.append((x, y))

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx >= dy else dy

    moves = [(0, 0)]
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            if dx == 0 and dy == 0:
                continue
            moves.append((dx, dy))

    legal = []
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obst:
            legal.append((dx, dy))
    if not legal:
        return [0, 0]

    if not resources:
        best = None
        bestv = None
        for dx, dy in legal:
            nx, ny = sx + dx, sy + dy
            score = cheb(nx, ny, ox, oy)
            if best is None or score > bestv:
                best, bestv = (dx, dy), score
        return [best[0], best[1]]

    # Choose move that maximizes advantage for the best contested resource this turn.
    best_move = (0, 0)
    best_key = None
    for dx, dy in legal:
        nx, ny = sx + dx, sy + dy
        best_for_move = None
        # Evaluate only the single resource that gives the best immediate contest advantage.
        for rx, ry in resources:
            sd = cheb(nx, ny, rx, ry)
            od = cheb(ox, oy, rx, ry)
            adv = od - sd
            # Prefer positive advantage; tie-break toward smaller self distance.
            key = (adv, -sd)
            if best_for_move is None or key > best_for_move:
                best_for_move = key
        # Secondary tie-break: prefer moves that get closer to some resource at all.
        overall_sd = min(cheb(nx, ny, rx, ry) for rx, ry in resources)
        key2 = (best_for_move[0], best_for_move[1], -overall_sd)
        if best_key is None or key2 > best_key:
            best_key, best_move = key2, (dx, dy)

    return [int(best_move[0]), int(best_move[1])]