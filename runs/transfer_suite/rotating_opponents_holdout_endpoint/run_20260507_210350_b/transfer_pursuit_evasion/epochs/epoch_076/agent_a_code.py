def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position", [0, 0]) or [0, 0]
    op = observation.get("opponent_position", [0, 0]) or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles", []) or []:
        if p is not None and len(p) >= 2:
            obstacles.add((int(p[0]), int(p[1])))

    role_self = str(observation.get("self_role", "") or "").lower()
    role_opp = str(observation.get("opponent_role", "") or "").lower()
    self_is_pursuer = any(k in role_self for k in ("pursuer", "chaser", "hunter"))
    opp_is_pursuer = any(k in role_opp for k in ("pursuer", "chaser", "hunter"))
    am_pursuer = self_is_pursuer if (self_is_pursuer or opp_is_pursuer) else True

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def blocked(x, y):
        return (x, y) in obstacles

    def dist(x, y, a, b):
        dx = x - a
        if dx < 0: dx = -dx
        dy = y - b
        if dy < 0: dy = -dy
        return dx if dx > dy else dy  # Chebyshev

    # Secondary target to break ties deterministically (corners).
    corners = [(w - 1, 0), (w - 1, h - 1), (0, h - 1), (0, 0)]
    target = corners[(int(observation.get("turn_index", 0)) // 2) % 4]
    if not am_pursuer:
        # For evasion, aim away from opponent.
        if dist(target[0], target[1], ox, oy) < dist(corners[(int(observation.get("turn_index", 0)) + 2) % 4][0], corners[(int(observation.get("turn_index", 0)) + 2) % 4][1], ox, oy):
            target = corners[(int(observation.get("turn_index", 0)) + 2) % 4]

    best = None
    best_move = [0, 0]
    order = 0

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or blocked(nx, ny):
            continue
        d = dist(nx, ny, ox, oy)
        if am_pursuer:
            # Prefer smaller distance; secondarily prefer moving toward target.
            primary = -d
            secondary = -(dist(nx, ny, target[0], target[1]))
        else:
            # Prefer larger distance; secondarily prefer moving toward target.
            primary = d
            secondary = -(dist(nx, ny, target[0], target[1]))

        key = (primary, secondary, -order)
        order += 1
        if best is None or key > best:
            best = key
            best_move = [dx, dy]

    if best is None:
        return [0, 0]
    return best_move