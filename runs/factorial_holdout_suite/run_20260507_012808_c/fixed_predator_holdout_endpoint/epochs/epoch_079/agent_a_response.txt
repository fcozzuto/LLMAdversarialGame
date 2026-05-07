def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = set()
    for p in observation.get("obstacles", []) or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for r in observation.get("resources", []) or []:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    if not resources:
        return [0, 0]

    def man(ax, ay, bx, by):
        return abs(ax - bx) + abs(ay - by)

    # Pick a target with deterministic "deny vs race" scoring.
    # Positive favors us: if we can arrive sooner, big reward; if not, penalize.
    best = None
    bs = None
    for rx, ry in resources:
        sd = man(sx, sy, rx, ry)
        od = man(ox, oy, rx, ry)
        lead = od - sd  # >0 means we are closer
        # Mild tie-break toward higher lead but also toward nearer targets.
        sc = 1000 * (1 if lead > 0 else 0) + 10 * lead - 0.05 * sd
        if bs is None or sc > bs or (sc == bs and (sd < best[0] if False else False)):
            best, bs = (rx, ry), sc

    tx, ty = best

    moves = [(dx, dy) for dx in (-1, 0, 1) for dy in (-1, 0, 1)]
    # Prefer diagonal toward target; deterministic tie-break by delta components.
    def move_key(m):
        dx, dy = m
        nx, ny = sx + dx, sy + dy
        diag_pref = 0 if (dx != 0 and dy != 0) else 1
        towards = -(abs(nx - tx) + abs(ny - ty))
        return (diag_pref, -towards, dx, dy)

    best_move = (0, 0)
    best_score = None
    for m in sorted(moves, key=move_key):
        dx, dy = m
        nx, ny = sx + dx, sy + dy
        if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles:
            # Prefer reducing our distance to target; if tie, prefer increasing distance from opponent target race
            sd2 = man(nx, ny, tx, ty)
            od2 = man(nx, ny, ox, oy)  # helps avoid getting blocked by opponent proximity
            score = (-sd2, od2, dx, dy)
            if best_score is None or score < best_score:
                best_score = score
                best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]