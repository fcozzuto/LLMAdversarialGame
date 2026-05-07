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
        cx, cy = (gw - 1) // 2, (gh - 1) // 2
        dx = 0 if sx == cx else (1 if cx > sx else -1)
        dy = 0 if sy == cy else (1 if cy > sy else -1)
        return [dx, dy]

    def cheb_dist(a, b, c, d):
        dx = a - c
        if dx < 0: dx = -dx
        dy = b - d
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    # Prefer resources where we can arrive strictly sooner; then closer.
    best = None
    for tx, ty in resources:
        sd = cheb_dist(sx, sy, tx, ty)
        od = cheb_dist(ox, oy, tx, ty)
        advantage = od - sd
        # If tie/advantage small, still prefer ones where opponent is not earlier.
        key = (advantage, -sd, tx, ty)
        if best is None or key > best[0]:
            best = (key, (tx, ty))
    tx, ty = best[1]

    moves = []
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            if not inb(nx, ny) or (nx, ny) in obs_set:
                continue
            nd_self = cheb_dist(nx, ny, tx, ty)
            nd_opp = cheb_dist(nx, ny, ox, oy)
            # Primary: reduce distance to target; secondary: keep opponent farther (slight).
            score = (-(nd_self * 10 + (0 if (nx, ny) == (sx, sy) else 0)), nd_opp, dx, dy)
            moves.append((score, [dx, dy]))
    if not moves:
        return [0, 0]
    moves.sort(reverse=True)
    return moves[0][1]