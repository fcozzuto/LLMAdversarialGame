def choose_move(observation):
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []

    obstacle_set = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obstacle_set.add((p[0], p[1]))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacle_set

    def dist(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx + dy

    if not resources:
        return [0, 0]

    # Choose a target with maximal distance advantage over opponent (not just closest).
    best = None
    best_key = (-10**9, 10**9)
    for rx, ry in resources:
        sd = dist(sx, sy, rx, ry)
        od = dist(ox, oy, rx, ry)
        key = (od - sd, -sd)
        if key[0] > best_key[0] or (key[0] == best_key[0] and key[1] > best_key[1]):
            best_key = key
            best = (rx, ry)

    tx, ty = best

    # Pick move that improves our distance; break ties by improving the distance advantage.
    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best_move = (0, 0)
    best_val = None
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        nsd = dist(nx, ny, tx, ty)
        nod = dist(ox, oy, tx, ty)
        advantage = nod - nsd
        # Prefer smaller distance to target; then larger advantage; then deterministic tie-break.
        val = (nsd, -advantage, dx, dy)
        if best_val is None or val < best_val:
            best_val = val
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]