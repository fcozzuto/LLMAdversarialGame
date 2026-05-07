def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    gw = int(observation.get("grid_width", 8))
    gh = int(observation.get("grid_height", 8))

    obs = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            px, py = int(p[0]), int(p[1])
            if 0 <= px < gw and 0 <= py < gh:
                obs.add((px, py))

    resources = []
    for r in observation.get("resources") or []:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            rx, ry = int(r[0]), int(r[1])
            if 0 <= rx < gw and 0 <= ry < gh and (rx, ry) not in obs:
                resources.append((rx, ry))
    if not resources:
        return [0, 0]

    def md(a, b, c, d):
        dx = a - c
        if dx < 0: dx = -dx
        dy = b - d
        if dy < 0: dy = -dy
        return dx + dy

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    best = None
    best_key = None
    for rx, ry in resources:
        sd = md(sx, sy, rx, ry)
        od = md(ox, oy, rx, ry)
        # Prefer resources we can reach no later; then minimize our distance; then maximize slack over opponent.
        key = (0 if sd <= od else 1, sd - od, sd, -(rx + ry))
        if best_key is None or key < best_key:
            best_key = key
            best = (rx, ry)

    tx, ty = best
    step_options = []
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if 0 <= nx < gw and 0 <= ny < gh and (nx, ny) not in obs:
            # Score step by improvement toward target, then avoid giving opponent a closer path.
            nsd = md(nx, ny, tx, ty)
            nod = md(ox, oy, tx, ty)
            # Softly discourage stepping adjacent to opponent (reduce interception risk).
            opp_adj = max(abs(nx - ox), abs(ny - oy))
            step_key = (nsd, nod - sd if False else 0, opp_adj, abs(dx) + abs(dy))
            step_options.append((step_key, (dx, dy)))
    if not step_options:
        return [0, 0]
    step_options.sort(key=lambda t: t[0])
    return [int(step_options[0][1][0]), int(step_options[0][1][1])]