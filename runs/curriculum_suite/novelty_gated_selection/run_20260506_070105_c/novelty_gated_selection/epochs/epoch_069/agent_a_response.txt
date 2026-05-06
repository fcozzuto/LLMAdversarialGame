def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (w - 1, h - 1))
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = set()
    for o in observation.get("obstacles", []) or []:
        if o is not None and len(o) >= 2:
            obstacles.add((int(o[0]), int(o[1])))

    resources = []
    for r in observation.get("resources", []) or []:
        if r is not None and len(r) >= 2:
            rx, ry = int(r[0]), int(r[1])
            if (rx, ry) not in obstacles:
                resources.append((rx, ry))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def man(ax, ay, bx, by):
        return abs(ax - bx) + abs(ay - by)

    if not resources:
        return [0, 0]

    # Choose a target that favors us reaching soon while staying relatively inconvenient to opponent.
    best_t = None
    best_tscore = None
    for tx, ty in resources:
        ds = man(sx, sy, tx, ty)
        do = man(ox, oy, tx, ty)
        edge = 1 if (tx == 0 or tx == w - 1 or ty == 0 or ty == h - 1) else 0
        # Lower is better
        tscore = ds * 10 - do * 6 + edge * 2
        if best_tscore is None or tscore < best_tscore:
            best_tscore, best_t = tscore, (tx, ty)

    tx, ty = best_t
    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best_move = [0, 0]
    best_score = None

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue
        ds2 = man(nx, ny, tx, ty)
        do = man(ox, oy, tx, ty)
        # Encourage decreasing our distance; discourage giving opponent an advantage.
        # Small tie-break to keep moves toward the target direction.
        align = -abs((tx - nx) * (tx - sx) + (ty - ny) * (ty - sy))
        score = ds2 * 8 - do * 4 + align * 0.0001
        if best_score is None or score < best_score:
            best_score, best_move = score, [dx, dy]

    if best_score is None:
        return [0, 0]
    return best_move