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
        if dx < 0:
            dx = -dx
        dy = y1 - y2
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    best = None
    best_key = None
    for rx, ry in sorted(resources):
        myd = kdist(sx, sy, rx, ry)
        if myd == 0:
            return [0, 0]
        opd = kdist(ox, oy, rx, ry)
        # Prefer resources where we arrive no later; otherwise prefer closest advantage.
        race_bonus = 1000 if myd <= opd else 0
        # Primary: maximize advantage and race bonus; secondary: minimize our distance; tertiary: maximize opponent distance.
        key = (race_bonus + (opd - myd), -myd, opd, -rx - ry)
        if best_key is None or key > best_key:
            best_key = key
            best = (rx, ry)

    tx, ty = best

    deltas = [(-1, -1), (0, -1), (1, -1),
              (-1, 0), (0, 0), (1, 0),
              (-1, 1), (0, 1), (1, 1)]
    best_move = (0, 0)
    best_move_key = None

    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if nx < 0 or nx >= w or ny < 0 or ny >= h:
            continue
        if (nx, ny) in blocked:
            continue
        myd2 = kdist(nx, ny, tx, ty)
        opd2 = kdist(ox, oy, tx, ty)
        # Keep deterministic and slightly reduce opponent's race position by improving our reach.
        key = (-myd2, (opd2 - myd2), -abs(ox - tx) - abs(oy - ty), dx * 3 + dy)
        if best_move_key is None or key > best_move_key:
            best_move_key = key
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]