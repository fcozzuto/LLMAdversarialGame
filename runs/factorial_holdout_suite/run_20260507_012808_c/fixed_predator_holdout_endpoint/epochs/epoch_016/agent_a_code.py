def choose_move(observation):
    w = int(observation["grid_width"])
    h = int(observation["grid_height"])
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]

    obstacles = set()
    for p in observation.get("obstacles", []) or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obstacles.add((int(p[0]), int(p[1])))

    resources = observation.get("resources", []) or []
    res = []
    for r in resources:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            rx, ry = int(r[0]), int(r[1])
            if 0 <= rx < w and 0 <= ry < h:
                res.append((rx, ry))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    moves = []
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            if inb(nx, ny) and (nx, ny) not in obstacles:
                moves.append((dx, dy))
    if not moves:
        return [0, 0]

    def md(ax, ay, bx, by):
        return abs(ax - bx) + abs(ay - by)

    # If no resources, drift away from opponent to reduce their interference.
    if not res:
        best = None
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            sc = md(nx, ny, ox, oy)
            if best is None or sc > best[0]:
                best = (sc, dx, dy)
        return [best[1], best[2]]

    # Primary: pick move that maximizes advantage on the best contested resource.
    best = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        my_next_dist = md(nx, ny, ox, oy)
        one_step_score = 0
        for (rx, ry) in res:
            if nx == rx and ny == ry:
                one_step_score += 1000  # immediate pickup preference
        best_adv_for_move = None
        for (rx, ry) in res:
            sd = md(nx, ny, rx, ry)
            od = md(ox, oy, rx, ry)
            # Prefer winning/closing on resources, and slightly prefer reducing opp's lead.
            adv = (od - sd) - 0.02 * sd
            if best_adv_for_move is None or adv > best_adv_for_move:
                best_adv_for_move = adv
        # Secondary: if not picking up immediately, still avoid stepping into "opponent proximity"
        # too much (helpful vs deniers who get turns hitting resources).
        proximity_penalty = 0.01 * my_next_dist
        sc = one_step_score + (best_adv_for_move * 50) - proximity_penalty
        if best is None or sc > best[0]:
            best = (sc, dx, dy)
    return [best[1], best[2]]