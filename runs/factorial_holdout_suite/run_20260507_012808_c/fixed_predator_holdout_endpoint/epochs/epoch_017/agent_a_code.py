def choose_move(observation):
    w = int(observation["grid_width"]); h = int(observation["grid_height"])
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

    def inb(x, y): return 0 <= x < w and 0 <= y < h
    def md(x1, y1, x2, y2): return abs(x1 - x2) + abs(y1 - y2)

    moves = []
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            if inb(nx, ny) and (nx, ny) not in obstacles:
                moves.append((dx, dy))
    if not moves:
        return [0, 0]
    if not res:
        # Drift to improve survival: maximize distance from opponent.
        best = None
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            sc = md(nx, ny, ox, oy)
            if best is None or sc > best[0] or (sc == best[0] and (dx, dy) < best[1]):
                best = (sc, (dx, dy))
        return [best[1][0], best[1][1]]

    # Choose a target with best "lead": prefer where we are closer than opponent.
    best_t = None
    for rx, ry in res:
        sd = md(sx, sy, rx, ry)
        od = md(ox, oy, rx, ry)
        lead = od - sd
        # If no clear lead, still prefer nearer resources deterministically.
        key = (lead, -sd, -rx, -ry)
        if best_t is None or key > best_t[0]:
            best_t = (key, (rx, ry))
    tx, ty = best_t[1]

    # If opponent is already closer, de-prioritize this target and go for next-best deterministically.
    sd0 = md(sx, sy, tx, ty)
    od0 = md(ox, oy, tx, ty)
    if od0 < sd0:
        best_t2 = None
        for rx, ry in res:
            sd = md(sx, sy, rx, ry); od = md(ox, oy, rx, ry)
            lead = od - sd
            key = (lead, -sd, -rx, -ry)
            if best_t2 is None or key > best_t2[0]:
                best_t2 = (key, (rx, ry))
        tx, ty = best_t2[1]

    # Score candidate moves by how they help us reach target while not walking into opponent.
    best = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        d_to_t = md(nx, ny, tx, ty)
        d_to_o = md(nx, ny, ox, oy)
        # Encourage blocking-like behavior: if close to opponent, move away; otherwise focus on target.
        sc = (-d_to_t * 3) + (d_to_o * (2 if d_to_o <= 2 else 1)) - (dx == 0 and dy == 0) * 1
        if best is None or sc > best[0] or (sc == best[0] and (dx, dy) < best[1]):
            best = (sc, (dx, dy))
    return [best[1][0], best[1][1]]