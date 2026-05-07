def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
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

    def md(ax, ay, bx, by):
        return abs(ax - bx) + abs(ay - by)

    # Prefer resources where we are earlier; otherwise contest the one where we are closest (or least behind).
    best = None
    best_key = None
    for rx, ry in resources:
        sd = md(sx, sy, rx, ry)
        od = md(ox, oy, rx, ry)
        key = (od - sd, -sd, -od, rx, ry)  # deterministic
        if best_key is None or key > best_key:
            best_key = key
            best = (rx, ry)

    tx, ty = best
    if sx == tx and sy == ty:
        return [0, 0]

    # One-step obstacle-aware move towards target with deterministic tie-break.
    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    bestm = None
    bestk = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h):
            continue
        if (nx, ny) in obstacles:
            continue
        # If the cell is good for contesting: also lightly consider opponent distance reduction.
        d_self = md(nx, ny, tx, ty)
        d_opp = md(nx, ny, ox, oy)
        d_tx_opp = md(ox, oy, tx, ty)
        # Prefer minimizing our distance to target; if equal, prefer increasing opponent distance to that target.
        key = (-(d_self), (d_tx_opp - d_opp), -abs(tx - nx) - abs(ty - ny), dx, dy)
        if bestk is None or key > bestk:
            bestk = key
            bestm = (dx, dy)

    if bestm is None:
        return [0, 0]
    return [int(bestm[0]), int(bestm[1])]