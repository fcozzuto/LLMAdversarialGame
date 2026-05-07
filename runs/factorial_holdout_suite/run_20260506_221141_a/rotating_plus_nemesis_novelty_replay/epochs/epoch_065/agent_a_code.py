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

    res = []
    for r in observation.get("resources") or []:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            rx, ry = int(r[0]), int(r[1])
            if inb(rx, ry) and (rx, ry) not in obs_set:
                res.append((rx, ry))
    if not res:
        return [0, 0]

    def md(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx + dy

    # Target: maximize (opponent lead - self lead) so we race where we are closer.
    best = None
    for tx, ty in res:
        sd = md(sx, sy, tx, ty)
        od = md(ox, oy, tx, ty)
        adv = od - sd
        cand = (adv, -sd, tx, ty)
        if best is None or cand > best:
            best = cand
    tx, ty = best[2], best[3]

    # Local move choice with obstacle avoidance.
    moves = []
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            if not inb(nx, ny) or (nx, ny) in obs_set:
                continue
            self_next = md(nx, ny, tx, ty)
            opp_next = md(ox, oy, tx, ty)
            # Prefer reducing our distance; break ties by improving race advantage; then by deterministic order.
            goal = (-self_next, opp_next - self_next, -abs(nx - ox), -abs(ny - oy), dx, dy)
            moves.append((goal, dx, dy))
    if not moves:
        return [0, 0]
    moves.sort(reverse=True)
    return [int(moves[0][1]), int(moves[0][2])]