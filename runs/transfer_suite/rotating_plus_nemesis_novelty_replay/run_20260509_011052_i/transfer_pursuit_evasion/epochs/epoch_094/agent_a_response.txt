def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    obstacles = observation.get("obstacles") or []
    obs = set((p[0], p[1]) for p in obstacles)

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def ok(x, y):
        return inb(x, y) and (x, y) not in obs

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    corners = [(0, 0), (0, h - 1), (w - 1, 0), (w - 1, h - 1)]

    def dist2(x, y, a, b):
        dx = x - a
        dy = y - b
        return dx * dx + dy * dy

    pursue = ((observation.get("self_role") or "").lower() != "evader")

    if pursue:
        # Flank to a corner farthest from opponent while still closing distance.
        tx, ty = max(corners, key=lambda c: dist2(c[0], c[1], ox, oy))
        prefer = lambda nx, ny: (-dist2(nx, ny, ox, oy), -dist2(nx, ny, tx, ty))
        maximize = False  # minimize tuple
    else:
        # Run to a corner farthest from opponent; also avoid getting closer.
        tx, ty = max(corners, key=lambda c: dist2(c[0], c[1], ox, oy))
        prefer = lambda nx, ny: (dist2(nx, ny, ox, oy), -dist2(nx, ny, tx, ty))
        maximize = True

    best = (None, None)
    best_key = None

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not ok(nx, ny):
            continue
        dopp = dist2(nx, ny, ox, oy)
        # Slightly discourage stepping into positions that reduce corner progress for both roles.
        key = prefer(nx, ny)
        # Hard prefer immediate capture check (only if capture were possible with radius 0).
        if dnx := dopp == 0:
            key = (-10**18, -10**18) if pursue else (10**18, 10**18)
        if best_key is None or ((key < best_key) if not maximize else (key > best_key)):
            best_key = key
            best = (dx, dy)
        elif key == best_key and best_key is not None:
            # Deterministic tie-break toward smaller |dx| then smaller |dy| then fixed direction order.
            if abs(dx) < abs(best[0]) or (abs(dx) == abs(best[0]) and abs(dy) < abs(best[1])):
                best = (dx, dy)

    if best == (None, None):
        return [0, 0]
    return [int(best[0]), int(best[1])]