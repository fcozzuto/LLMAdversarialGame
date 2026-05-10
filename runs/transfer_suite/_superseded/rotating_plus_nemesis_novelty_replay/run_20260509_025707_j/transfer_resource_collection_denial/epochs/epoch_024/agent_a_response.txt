def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    resources = observation.get("resources", []) or []
    obstacles_list = observation.get("obstacles", []) or []
    obstacles = set((p[0], p[1]) for p in obstacles_list)

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    if not resources:
        return [0, 0]

    def man(ax, ay, bx, by):
        d = ax - bx
        if d < 0: d = -d
        e = ay - by
        if e < 0: e = -e
        return d + e

    # Pick best resource to maximize our ability to secure it first, with small denial bias.
    best = None
    best_key = None
    for rx, ry in resources:
        sd = man(sx, sy, rx, ry)
        od = man(ox, oy, rx, ry)
        # We want (od - sd) large: we are closer; also favor nearer targets.
        # Denial tweak: if opponent is very close, prioritize it more (to prevent grabs).
        contest = od - sd
        urgent = 0
        if od <= sd:
            urgent = 2 + (3 if od == sd else 0)
        # Encourage moving along opponent's axis a bit (resource_denier tends to contest front).
        align = 0
        if ry == oy: align += 1
        if rx == ox: align += 0.5
        key = (-(contest + urgent + align), sd, rx * 16 + ry)
        if best_key is None or key < best_key:
            best_key = key
            best = (rx, ry)

    tx, ty = best
    # If we're already on a resource cell, do nothing.
    if sx == tx and sy == ty:
        return [0, 0]

    # Choose next step: among valid moves, minimize our distance to target; tie-break to push away opponent.
    moves = []
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            if not inb(nx, ny):
                continue
            d_to_t = man(nx, ny, tx, ty)
            d_opp = man(nx, ny, ox, oy)
            # Also discourage stepping away from target when close.
            step_pen = (d_to_t > man(sx, sy, tx, ty))
            key = (d_to_t, step_pen, -d_opp, (dx == 0 and dy == 0))
            moves.append((key, dx, dy))

    if not moves:
        return [0, 0]
    moves.sort(key=lambda x: x[0])
    return [int(moves[0][1]), int(moves[0][2])]