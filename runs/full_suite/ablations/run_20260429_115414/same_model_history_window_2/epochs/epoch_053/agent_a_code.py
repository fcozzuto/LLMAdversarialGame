def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sp = observation.get("self_position", (0, 0))
    op = observation.get("opponent_position", (0, 0))
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

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    center = ((w - 1) // 2, (h - 1) // 2)

    def valid(nx, ny):
        return 0 <= nx < w and 0 <= ny < h and (nx, ny) not in blocked

    best = (0, 0)
    best_val = -10**18
    opp_dist_now = cheb(sx, sy, ox, oy)

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue

        if resources:
            best_t = -10**18
            for rx, ry in resources:
                d_self = cheb(nx, ny, rx, ry)
                d_opp = cheb(ox, oy, rx, ry)
                on_res = 1 if (nx == rx and ny == ry) else 0
                # Prefer targets we're closer to; discourage letting opponent get there first.
                tval = 5000 * on_res + (d_opp - d_self) * 25 - d_self
                best_t = tval if tval > best_t else best_t
            # Small tie-break: keep relative distance to opponent reasonable (avoid easy interceptions)
            tiebreak = (cheb(nx, ny, ox, oy) - opp_dist_now) * 2
            val = best_t + tiebreak
        else:
            # No visible resources: return toward center while avoiding obstacles.
            dcen = cheb(nx, ny, center[0], center[1])
            dopp = cheb(nx, ny, ox, oy)
            val = -dcen * 10 + dopp * 1

        if val > best_val:
            best_val = val
            best = (dx, dy)

    return [int(best[0]), int(best[1])]