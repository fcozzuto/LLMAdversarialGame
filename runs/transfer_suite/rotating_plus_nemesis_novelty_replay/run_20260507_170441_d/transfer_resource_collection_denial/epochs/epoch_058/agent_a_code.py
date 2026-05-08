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

    best_t = None
    for rx, ry in resources:
        my_d = dist8(sx, sy, rx, ry)
        op_d = dist8(ox, oy, rx, ry)
        adv = my_d - op_d  # negative => we are ahead (we arrive sooner)
        # prefer ahead; then closer to us; then deterministic coord
        key = (adv, my_d, rx, ry)
        if best_t is None or key < best_t[0]:
            best_t = (key, (rx, ry))
    tx, ty = best_t[1]

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    candidates = []
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        my_d = dist8(nx, ny, tx, ty)
        op_d = dist8(ox, oy, tx, ty)
        # minimize our remaining distance; if tie, prefer states that keep us ahead overall
        key = (my_d, (my_d - op_d), nx, ny)
        candidates.append((key, (dx, dy)))
    candidates.sort(key=lambda t: t[0])
    return list(candidates[0][1])