def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [w - 1, h - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    blocked = set()
    for b in observation.get("obstacles") or []:
        if b and len(b) >= 2:
            bx, by = int(b[0]), int(b[1])
            if 0 <= bx < w and 0 <= by < h:
                blocked.add((bx, by))

    resources = []
    for r in observation.get("resources") or []:
        if r and len(r) >= 2:
            rx, ry = int(r[0]), int(r[1])
            if 0 <= rx < w and 0 <= ry < h and (rx, ry) not in blocked:
                resources.append((rx, ry))

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0:
            dx = -dx
        dy = y1 - y2
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    legal = []
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in blocked:
            legal.append((nx, ny, dx, dy))
    if not legal:
        return [0, 0]

    if resources:
        # Choose a target resource deterministically: min cheb distance, then lexicographic
        best_t = None
        best_td = None
        for rx, ry in resources:
            d = cheb(sx, sy, rx, ry)
            if best_td is None or d < best_td or (d == best_td and (rx, ry) < best_t):
                best_td = d
                best_t = (rx, ry)
        tx, ty = best_t
    else:
        # If no resources visible, head toward center-ish while also keeping away from opponent
        tx, ty = w // 2, h // 2

    best = None
    for nx, ny, dx, dy in legal:
        d_self = cheb(nx, ny, tx, ty)
        d_opp = cheb(ox, oy, tx, ty)
        d_opp_after = cheb(ox, oy, tx, ty)  # opponent doesn't move this turn; use current as baseline
        # Estimate whether our move makes it easier for opponent by checking if our move is closer than ours currently
        d_self_now = cheb(sx, sy, tx, ty)
        closer_than_now = 1 if d_self < d_self_now else 0

        # Primary: reduce distance to target; Secondary: avoid letting opponent potentially be closer (based on distance gap)
        gap_now = d_self_now - d_opp
        gap_after = d_self - d_opp

        # Tie-breakers: prefer increasing distance to opponent and prefer lexicographically smaller dx,dy for determinism
        dist_to_opp = cheb(nx, ny, ox, oy)
        on_resource = 1 if (nx, ny) == (tx, ty) else 0

        # Lower tuple is better
        cand = (
            d_self,
            -on_resource,
            gap_after,
            -dist_to_opp,
            0 if closer_than_now else 1,
            dx,
            dy,
        )
        if best is None or cand < best[0]:
            best = (cand, dx, dy)

    return [int(best[1]), int(best[2])]