def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position", [0, 0]) or [0, 0]
    op = observation.get("opponent_position", [0, 0]) or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    blocked = set()
    for b in observation.get("obstacles", []) or []:
        if isinstance(b, (list, tuple)) and len(b) >= 2:
            bx, by = int(b[0]), int(b[1])
            if 0 <= bx < w and 0 <= by < h:
                blocked.add((bx, by))

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def safe(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in blocked

    def manh(x, y, a, b):
        return abs(x - a) + abs(y - b)

    role = str(observation.get("self_role", "") or "").lower()
    is_evader = ("evader" in role) or (role.endswith("e"))
    is_pursuer = ("pursuer" in role) or (role.endswith("p"))

    def mobility(x, y):
        c = 0
        for dx, dy in moves:
            nx, ny = x + dx, y + dy
            if safe(nx, ny):
                c += 1
        return c

    corners = [(0, 0), (w - 1, 0), (0, h - 1), (w - 1, h - 1)]
    phase = int(observation.get("turn_index", 0) or 0) % 4
    target = corners[phase]
    # If target is not a good separator, pick the corner farthest from opponent.
    cur_sep = manh(target[0], target[1], ox, oy)
    best_sep = cur_sep
    for tx, ty in corners:
        d = manh(tx, ty, ox, oy)
        if d > best_sep:
            best_sep = d
            target = (tx, ty)

    best = None
    best_m = [0, 0]
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not safe(nx, ny):
            continue
        d = manh(nx, ny, ox, oy)
        mob = mobility(nx, ny)
        # Evader: maximize separation and avoid mobility traps.
        # Pursuer: minimize separation and avoid low-mobility squares.
        sep_score = d if is_evader or not is_pursuer else -d
        # Slightly bias towards/away from corner depending on role.
        corner_bias = -manh(nx, ny, target[0], target[1])
        if not (is_evader or not is_pursuer):
            corner_bias = -corner_bias
        score = sep_score * 10 + mob * 2 + corner_bias

        if best is None or score > best or (score == best and (dx, dy) == (0, 0) and best_m != [0, 0]):
            best = score
            best_m = [dx, dy]

    return [int(best_m[0]), int(best_m[1])]