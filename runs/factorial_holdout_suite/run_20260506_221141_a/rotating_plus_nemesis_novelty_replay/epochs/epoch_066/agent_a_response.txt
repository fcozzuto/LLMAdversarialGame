def choose_move(observation):
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    gw = int(observation.get("grid_width", 8) or 8)
    gh = int(observation.get("grid_height", 8) or 8)

    def inb(x, y):
        return 0 <= x < gw and 0 <= y < gh

    obs_set = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            px, py = int(p[0]), int(p[1])
            if inb(px, py):
                obs_set.add((px, py))

    resources = []
    for r in observation.get("resources") or []:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            rx, ry = int(r[0]), int(r[1])
            if inb(rx, ry) and (rx, ry) not in obs_set:
                resources.append((rx, ry))

    if not resources:
        tx, ty = (gw - 1) // 2, (gh - 1) // 2
    else:
        def md(x1, y1, x2, y2):
            dx = x1 - x2
            if dx < 0: dx = -dx
            dy = y1 - y2
            if dy < 0: dy = -dy
            return dx + dy

        best = None
        best_key = None
        for tx, ty in resources:
            sd = md(sx, sy, tx, ty)
            od = md(ox, oy, tx, ty)
            adv = od - sd
            # Prefer positive advantage, then shortest self distance, then deterministic position tie-break
            key = (adv, -sd, -tx, -ty)
            if best_key is None or key > best_key:
                best_key = key
                best = (tx, ty)
        tx, ty = best

    deltas = []
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            if inb(nx, ny) and (nx, ny) not in obs_set:
                deltas.append((dx, dy))

    if not deltas:
        return [0, 0]

    def md2(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx + dy

    # Deterministic tie-breaking: same score -> smaller dx then dy lexicographically
    best_move = None
    best_score = None
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        self_d = md2(nx, ny, tx, ty)
        opp_d = md2(ox, oy, tx, ty)
        adv = opp_d - self_d
        # small additional pressure to move if already on target: keep collecting nearby by reducing self_d anyway
        score = (adv, -self_d, -abs(nx - tx), -abs(ny - ty), -dx, -dy)
        if best_score is None or score > best_score:
            best_score = score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]