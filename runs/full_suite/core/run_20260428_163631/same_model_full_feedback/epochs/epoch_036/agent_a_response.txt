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

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    cand = []
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if inb(nx, ny):
            cand.append((dx, dy, nx, ny))
    if not cand:
        return [0, 0]

    t = int(observation.get("turn_index") or 0)
    # Deterministic mild bias: early game prefer escaping toward center, late game prefer speed to resources.
    center_x = (w - 1) // 2
    center_y = (h - 1) // 2
    center_weight = 0.6 if t < 12 else 0.2

    best_move = (0, 0, sx, sy)
    best_score = -10**18

    if resources:
        for dx, dy, nx, ny in cand:
            score = 0
            # Choose best "swing" target: maximize (opponent distance advantage we create) and proximity to it.
            best_target = -10**18
            for rx, ry in resources:
                ds = cheb(nx, ny, rx, ry)
                do = cheb(ox, oy, rx, ry)
                # We want ds small and also (do - ds) large (deny opponent).
                val = (do - ds) * 10 - ds
                # Small tie-break toward center for determinism and to avoid dithering.
                val += -center_weight * cheb(nx, ny, center_x, center_y)
                if val > best_target:
                    best_target = val
            score = best_target
            # Extra deterministic tie-break: prefer not stepping adjacent to obstacles corner-traps.
            # (Simple: penalize moves that increase distance to center slightly when resources are scarce.)
            if len(resources) < 4:
                score += -0.5 * cheb(nx, ny, center_x, center_y)
            if score > best_score:
                best_score = score
                best_move = (dx, dy, nx, ny)
    else:
        # No visible resources: drift toward center while keeping far from opponent (avoid confrontation).
        for dx, dy, nx, ny in cand:
            score = cheb(nx, ny, center_x, center_y) * -1 - 0.3 * cheb(nx, ny, ox, oy)
            if score > best_score:
                best_score = score
                best_move = (dx, dy, nx, ny)

    return [int(best_move[0]), int(best_move[1])]