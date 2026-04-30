def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sx, sy = observation.get("self_position") or (0, 0)
    ox, oy = observation.get("opponent_position") or (0, 0)
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    blocked = set()
    for p in observation.get("obstacles") or []:
        if p and len(p) >= 2:
            bx, by = int(p[0]), int(p[1])
            if 0 <= bx < w and 0 <= by < h:
                blocked.add((bx, by))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in blocked

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0:
            dx = -dx
        dy = ay - by
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    resources = []
    for r in observation.get("resources") or []:
        if r and len(r) >= 2:
            rx, ry = int(r[0]), int(r[1])
            if 0 <= rx < w and 0 <= ry < h and (rx, ry) not in blocked:
                resources.append((rx, ry))
    if not resources:
        for dx, dy in [(1, 1), (0, 1), (1, 0), (0, 0), (-1, 0), (0, -1), (-1, -1), (1, -1), (-1, 1)]:
            nx, ny = sx + dx, sy + dy
            if inb(nx, ny):
                return [dx, dy]
        return [0, 0]

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    moves.sort(key=lambda t: (-(t[0] * (ox - sx) + t[1] * (oy - sy)), t[0], t[1]))

    best_move = (0, 0)
    best_val = -10**18
    opp_threat = 1.25

    # Evaluate "who can reach what next": maximize summed advantage over resources.
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue

        total = 0.0
        nearest = 10**9
        for rx, ry in resources:
            d_self = cheb(nx, ny, rx, ry)
            d_opp = cheb(ox, oy, rx, ry)
            if d_self == 0:
                total += 1e6
                continue
            nearest = d_self if d_self < nearest else nearest
            adv = d_opp - d_self  # positive means we are closer than opponent
            wgt = 1.0 / (1.0 + d_self)
            total += wgt * (adv - opp_threat * (d_self > d_opp))
        total -= 0.35 * nearest

        # Tie-break deterministically toward the move with smallest distance to the globally "most threatened" resource
        if total > best_val:
            best_val = total
            best_move = (dx, dy)
        elif total == best_val:
            tr = min(resources, key=lambda r: cheb(ox, oy, r[0], r[1]) - cheb(sx, sy, r[0], r[1]))
            dcur = cheb(nx, ny, tr[0], tr[1])
            bestnx, bestny = sx + best_move[0], sy + best_move[1]
            dbest = cheb(bestnx, bestny, tr[0], tr[1])
            if dcur < dbest:
                best_move = (dx, dy)

    # If every candidate was invalid, fall back.
    if not inb(sx + best_move[0], sy + best_move[1]):
        return [0, 0]
    return [int(best_move[0]), int(best_move[1])]