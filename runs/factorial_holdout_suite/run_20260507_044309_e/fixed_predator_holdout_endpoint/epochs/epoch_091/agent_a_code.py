def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])
    turns_remaining = int(observation.get("turns_remaining") or 0)
    resources = observation.get("resources") or []
    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            px, py = int(p[0]), int(p[1])
            if 0 <= px < w and 0 <= py < h:
                obstacles.add((px, py))

    def man(a, b, c, d):
        return abs(a - c) + abs(b - d)

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    if not resources:
        return [0, 0]

    best = None
    best_key = None
    for r in resources:
        rx, ry = int(r[0]), int(r[1])
        if (rx, ry) in obstacles:
            continue
        sd = man(sx, sy, rx, ry)
        od = man(ox, oy, rx, ry)
        if sd > turns_remaining + 1:
            continue
        # Prefer: reachable, likely to arrive first; then closer to self; then farther from opponent.
        winlike = 1 if sd <= od else 0
        key = (winlike, -(sd), (od - sd), -od, -abs(rx - rx), rx, ry)
        if best_key is None or key > best_key:
            best_key = key
            best = (rx, ry)

    if best is None:
        # Fallback: head to nearest non-obstacle resource.
        rx, ry = min(
            [(int(r[0]), int(r[1])) for r in resources if (int(r[0]), int(r[1])) not in obstacles] or [(sx, sy)],
            key=lambda t: man(sx, sy, t[0], t[1]),
        )
        best = (rx, ry)

    tx, ty = best
    if (sx, sy) == (tx, ty):
        return [0, 0]

    # Greedy one-step improvement among valid local moves (diagonal allowed).
    best_move = [0, 0]
    best_score = None
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            if not inb(nx, ny):
                continue
            if (nx, ny) in obstacles:
                continue
            self_d = man(nx, ny, tx, ty)
            opp_d = man(ox, oy, tx, ty)
            cur_sd = man(sx, sy, tx, ty)
            # Prefer lowering distance; slight preference to moves that keep us contesting.
            score = (self_d, cur_sd - self_d, -abs(opp_d - self_d), abs(ty - ny) + abs(tx - nx), -((nx - tx) ** 2 + (ny - ty) ** 2))
            if best_score is None or score < best_score:
                best_score = score
                best_move = [dx, dy]

    return [int(best_move[0]), int(best_move[1])]