def choose_move(observation):
    sp = observation.get("self_position", [0, 0]) or [0, 0]
    op = observation.get("opponent_position", [0, 0]) or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)

    obstacles = set()
    for o in observation.get("obstacles", []) or []:
        if isinstance(o, (list, tuple)) and len(o) >= 2:
            obstacles.add((int(o[0]), int(o[1])))

    resources = []
    for r in observation.get("resources", []) or []:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))
    if not resources:
        return [0, 0]

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    best = None
    best_key = None
    for rx, ry in resources:
        ds = cheb(sx, sy, rx, ry)
        do = cheb(ox, oy, rx, ry)
        # Prefer resources opponent is less able to reach; also avoid too far targets.
        score = (do - ds) * 1000 - ds
        # Deterministic tiebreak: closer to center slightly, then lexicographic.
        cx, cy = (w - 1) / 2.0, (h - 1) / 2.0
        center_bias = -cheb(rx, ry, int(cx), int(cy))
        key = (score + center_bias, -do, -ds, -rx, -ry)
        if best_key is None or key > best_key:
            best_key = key
            best = (rx, ry)

    tx, ty = best

    # Greedy step towards target, with obstacle-aware tie-breaking.
    moves = []
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            if dx == 0 and dy == 0:
                pass
            if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles:
                d = cheb(nx, ny, tx, ty)
                # Prefer moves that reduce opponent access too (discourage drifting into their line).
                opp_d = cheb(ox, oy, nx, ny)
                moves.append(((d, -opp_d, abs(nx - tx) + abs(ny - ty), dx, dy), dx, dy))
    if not moves:
        return [0, 0]
    moves.sort(reverse=False, key=lambda z: z[0])
    return [int(moves[0][1]), int(moves[0][2])]