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

    def d(x1, y1, x2, y2):
        dx = x1 - x2
        dy = y1 - y2
        return abs(dx) if abs(dx) > abs(dy) else (abs(dx) if abs(dx) == abs(dy) else max(abs(dx), abs(dy)))

    if not resources:
        return [0, 0]

    best_t = None
    best_key = None
    for rx, ry in resources:
        myd = max(abs(rx - sx), abs(ry - sy))
        opd = max(abs(rx - ox), abs(ry - oy))
        # Prefer resources we can arrive at no later than opponent; then get them sooner.
        key = (1 if myd <= opd else 0, -opd, myd, rx, ry)  # tuple smaller is better
        if best_key is None or key < best_key:
            best_key = key
            best_t = (rx, ry)

    tx, ty = best_t
    my_now = max(abs(tx - sx), abs(ty - sy))
    op_now = max(abs(tx - ox), abs(ty - oy))

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best_move = (0, 0)
    best_val = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        myd_next = max(abs(tx - nx), abs(ty - ny))
        opd_next = max(abs(tx - ox), abs(ty - oy))  # opponent move unknown; keep static
        # If we're behind, prioritize closing distance quickly; if ahead, keep minimizing distance.
        behind = 1 if my_now > op_now else 0
        val = (-myd_next, -behind, opd_next, dx, dy)
        if best_val is None or val < best_val:
            best_val = val
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]