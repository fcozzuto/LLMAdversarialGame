def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) == 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for r in observation.get("resources") or []:
        if isinstance(r, (list, tuple)) and len(r) == 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    dirs = [(-1, -1), (0, -1), (1, -1),
            (-1, 0), (0, 0), (1, 0),
            (-1, 1), (0, 1), (1, 1)]

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    # Choose best resource deterministically
    target = None
    if resources:
        best = None
        # Prefer resources where we are closer than opponent; tie-break by being closer to us,
        # then by farther from opponent (more likely to deny), then lexicographic.
        for rx, ry in resources:
            ds = cheb(sx, sy, rx, ry)
            do = cheb(ox, oy, rx, ry)
            lead = do - ds  # positive if we are closer
            key = (lead, -do, -ds, rx, ry)
            if best is None or key > best:
                best = key
                target = (rx, ry)

    # If no visible resources, head toward center/away from opponent deterministically
    if target is None:
        tx, ty = (w - 1) // 2, (h - 1) // 2
    else:
        tx, ty = target

    # Evaluate moves: minimize distance to target; secondary: avoid moving closer to opponent when tied;
    # tertiary: avoid corners/edges slightly; quaternary: deterministic tie by dx,dy order.
    best_move = (0, 0)
    best_score = None
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        dtn = cheb(nx, ny, tx, ty)
        dtc = cheb(nx, ny, ox, oy)

        # Score: lower is better. Make it deterministic with small edge penalty.
        edge_pen = (0 if 1 <= nx <= w - 2 else 1) + (0 if 1 <= ny <= h - 2 else 1)
        # If target exists, prefer also to improve relative advantage.
        if resources:
            my_adv = cheb(nx, ny, tx, ty) - cheb(ox, oy, tx, ty)
            score = (dtn, my_adv, dtc, edge_pen, dx, dy)
        else:
            # No resources: go toward center while keeping distance from opponent.
            score = (dtn, -dtc, edge_pen, dx, dy)

        if best_score is None or score < best_score:
            best_score = score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]