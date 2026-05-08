def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources") or []
    obstacles = observation.get("obstacles") or []
    obst = set((p[0], p[1]) for p in obstacles if p is not None)

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obst

    def dist8(x1, y1, x2, y2):
        dx = abs(x1 - x2)
        dy = abs(y1 - y2)
        return dx if dx > dy else dy

    if not resources:
        return [0, 0]

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best_key = None
    best_t = None

    for rx, ry in resources:
        my_d = dist8(sx, sy, rx, ry)
        op_d = dist8(ox, oy, rx, ry)
        adv = op_d - my_d  # bigger => we reach sooner
        key = (-adv, my_d, rx, ry)  # determinism
        if best_key is None or key < best_key:
            best_key = key
            best_t = (rx, ry)

    tx, ty = best_t
    candidates = []
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        d_to = dist8(nx, ny, tx, ty)
        my_adv_if = dist8(ox, oy, tx, ty) - dist8(nx, ny, tx, ty)
        # Prefer reducing distance; if tie, prefer stronger advantage; then stable ordering
        candidates.append(((d_to, -my_adv_if, dx, dy), [dx, dy]))
    if not candidates:
        return [0, 0]
    candidates.sort(key=lambda z: z[0])
    return candidates[0][1]