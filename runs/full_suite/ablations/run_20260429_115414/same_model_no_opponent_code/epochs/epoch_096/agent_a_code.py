def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [w - 1, h - 1]
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

    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    def man(a, b, c, d): return abs(a - c) + abs(b - d)

    best_resource = None
    best_key = None
    if resources:
        for rx, ry in resources:
            d1 = man(sx, sy, rx, ry)
            d2 = man(ox, oy, rx, ry)
            lead = d2 - d1
            tie = (lead, -d2)
            # Prefer resources where we're not behind; deterministic tie-break by position
            key = (lead < 0, -lead, d1, rx, ry)
            if best_key is None or key < best_key:
                best_key = key
                best_resource = (rx, ry)

    if best_resource is None:
        # No visible resources: move away from opponent if possible, else stay
        candidates = []
        for dx, dy in dirs:
            nx, ny = sx + dx, sy + dy
            if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles:
                candidates.append((man(nx, ny, ox, oy), dx, dy))
        candidates.sort(reverse=True)
        return [candidates[0][1], candidates[0][2]] if candidates else [0, 0]

    rx, ry = best_resource
    best_move = None
    best_val = None
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h) or (nx, ny) in obstacles:
            continue
        d_ours = man(nx, ny, rx, ry)
        d_opp = man(ox, oy, rx, ry)
        # Also slightly prefer moves that avoid giving opponent advantage elsewhere
        val = (-d_ours, -abs(nx - ox) - abs(ny - oy), -d_opp, nx, ny)
        if best_val is None or val > best_val:
            best_val = val
            best_move = (dx, dy)

    return [best_move[0], best_move[1]] if best_move else [0, 0]