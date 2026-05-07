def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
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

    def dist2(a, b, c, d):
        dx = a - c
        dy = b - d
        return dx * dx + dy * dy

    # Pick target that maximizes our advantage (being closer than opponent), with tie-break on closeness.
    best = None
    best_key = None
    for rx, ry in resources:
        sd = dist2(sx, sy, rx, ry)
        od = dist2(ox, oy, rx, ry)
        # Advantage: smaller sd, larger od; prioritize immediate advantage strongly.
        key = (od - sd, -sd, rx, ry)
        if best_key is None or key > best_key:
            best_key = key
            best = (rx, ry)

    rx, ry = best

    deltas = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    best_move = (0, 0)
    best_move_key = None
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h):
            continue
        if (nx, ny) in obstacles:
            continue
        nd_self = dist2(nx, ny, rx, ry)
        nd_opp = dist2(ox, oy, rx, ry)
        # Prefer moves that reduce our distance to the chosen target and increase our lead.
        key = (nd_opp - nd_self, -nd_self, -abs(nx - rx) - abs(ny - ry), dx, dy)
        if best_move_key is None or key > best_move_key:
            best_move_key = key
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]