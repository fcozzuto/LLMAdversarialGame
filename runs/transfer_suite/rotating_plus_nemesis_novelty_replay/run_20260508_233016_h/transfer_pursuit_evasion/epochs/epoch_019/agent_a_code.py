def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sx, sy = observation.get("self_position") or [0, 0]
    ox, oy = observation.get("opponent_position") or [0, 0]
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    blocked = set()
    for p in observation.get("obstacles", []) or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            bx, by = int(p[0]), int(p[1])
            if 0 <= bx < w and 0 <= by < h:
                blocked.add((bx, by))

    resources = observation.get("resources", []) or []
    if not resources and isinstance(observation.get("remaining_resource_count"), int):
        resources = []

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def score_to_target(nx, ny, tx, ty):
        dx, dy = nx - tx, ny - ty
        if dx < 0:
            dx = -dx
        if dy < 0:
            dy = -dy
        return dx if dx >= dy else dy

    targets = []
    for r in resources:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            rx, ry = int(r[0]), int(r[1])
            if inb(rx, ry) and (rx, ry) not in blocked:
                targets.append((rx, ry))
    if targets:
        tx, ty = min(targets, key=lambda p: (score_to_target(sx, sy, p[0], p[1]), p[0], p[1]))
        prefer = "resource"
    else:
        tx, ty = ox, oy
        prefer = "opponent"

    best = None
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in blocked:
            continue
        d = score_to_target(nx, ny, tx, ty)
        tie = abs(nx - tx) + abs(ny - ty) if prefer == "resource" else (abs(nx - ox) + abs(ny - oy))
        key = (d, tie, dx, dy)
        if best is None or key < best[0]:
            best = (key, [dx, dy])

    if best is None:
        return [0, 0]
    return best[1]