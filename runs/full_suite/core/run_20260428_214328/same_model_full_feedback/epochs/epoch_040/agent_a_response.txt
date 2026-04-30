def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

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

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    if not resources:
        return [0, 0]

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def man(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    # Deterministic center bias to break ties.
    cx, cy = (w - 1) / 2.0, (h - 1) / 2.0
    best_val = -10**18
    best_move = (0, 0)

    # Heuristic: maximize opponent distance advantage after move;
    # secondary: move closer to the chosen best resource; tertiary: closer to center.
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue

        cur_best = -10**18
        for rx, ry in resources:
            du = man(nx, ny, rx, ry)
            dov = man(ox, oy, rx, ry)
            # Prefer positions that make us relatively closer (bigger gap).
            val = (dov - du) * 100 - du
            # Avoid walking into "traps": if opponent is extremely near a resource,
            # we weight it slightly less unless we can match/surpass their proximity.
            if dov <= 1:
                val -= 40
            # Small center bias for smoother movement
            val -= int((abs(nx - cx) + abs(ny - cy)) * 0.01)
            if val > cur_best:
                cur_best = val

        if cur_best > best_val:
            best_val = cur_best
            best_move = (dx, dy)
        elif cur_best == best_val:
            # Deterministic tie-breaker: prefer smaller dx, then smaller dy, then staying still.
            if (abs(dx), abs(dy), dx, dy) < (abs(best_move[0]), abs(best_move[1]), best_move[0], best_move[1]):
                best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]