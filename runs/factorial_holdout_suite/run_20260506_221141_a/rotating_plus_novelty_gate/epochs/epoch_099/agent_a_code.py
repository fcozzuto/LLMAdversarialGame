def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0]) or [0, 0]
    ox, oy = observation.get("opponent_position", [w - 1, h - 1]) or [w - 1, h - 1]
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    blocked = set()
    for p in observation.get("obstacles", []) or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                blocked.add((x, y))

    resources = []
    for p in observation.get("resources", []) or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in blocked:
                resources.append((x, y))
    if not resources:
        return [0, 0]

    def kdist(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    # Pick target resource with strongest race advantage; tie-break deterministically.
    best_rx, best_ry = resources[0]
    best = None
    # Evaluate all resources deterministically ordered
    for rx, ry in sorted(resources):
        sd = kdist(sx, sy, rx, ry)
        od = kdist(ox, oy, rx, ry)
        if sd == 0:
            return [0, 0]
        # Prefer winning race (sd < od); then prefer larger gap; then smaller sd.
        # If both don't win, prefer smaller od-sd (deny) and larger own progress.
        win = 1 if sd < od else 0
        gap = (od - sd)
        # Construct a lexicographic score tuple (higher is better)
        score = (win, gap, -sd, -(rx + 31 * ry))
        if best is None or score > best:
            best = score
            best_rx, best_ry = rx, ry

    tx, ty = best_rx, best_ry

    # Move one step toward target using king distance, avoid stepping into obstacles when possible.
    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best_move = (0, 0)
    best_val = None
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h):
            continue
        if (nx, ny) in blocked:
            continue
        nd = kdist(nx, ny, tx, ty)
        # Value: reduce distance first; if equal, prefer also making opponent farther.
        nop = kdist(ox, oy, tx, ty)
        # If we can reach (or stay) quickly, prioritize capturing now.
        val = (-nd, (nop - nd), -(abs(tx - nx) + abs(ty - ny)), -(dx * 3 + dy))
        if best_val is None or val > best_val:
            best_val = val
            best_move = (dx, dy)

    # If all moves blocked, stay.
    return [int(best_move[0]), int(best_move[1])]