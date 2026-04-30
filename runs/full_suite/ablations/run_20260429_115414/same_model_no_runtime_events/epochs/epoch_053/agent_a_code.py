def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [w - 1, h - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for p in observation.get("resources") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    rem = observation.get("remaining_resource_count", 0)
    try:
        rem = int(rem or 0)
    except:
        rem = 0
    late = rem <= 4

    if resources:
        best = None
        for rx, ry in resources:
            ds = cheb(sx, sy, rx, ry)
            do = cheb(ox, oy, rx, ry)
            # Prefer resources closer to us, and (slightly) farther from opponent.
            score = ds * 20 - do
            if best is None or score < best[0] or (score == best[0] and (rx, ry) < best[1]):
                best = (score, (rx, ry))
        tx, ty = best[1]
        # In late game, commit more directly.
        w_to = 50 if late else 20
        w_avoid = 12 if late else 6
    else:
        # No visible resources: drift to corner that is farther from opponent.
        corners = [(0, 0), (w - 1, 0), (0, h - 1), (w - 1, h - 1)]
        tx, ty = max(corners, key=lambda c: (cheb(c[0], c[1], ox, oy), -abs(c[0] - sx) - abs(c[1] - sy)))

        w_to = 25
        w_avoid = 15

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    bestm = None
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            nx, ny = sx, sy  # engine would keep us; evaluate as stay if blocked.

        # Move-to-target utility.
        ds2 = cheb(nx, ny, tx, ty)
        ds0 = cheb(sx, sy, tx, ty)

        # Avoid opponent when it is close.
        do2 = cheb(nx, ny, ox, oy)
        do0 = cheb(sx, sy, ox, oy)
        opp_push = (do2 - do0)

        # Tie-break to reduce dx then dy toward target.
        txd = abs(nx - tx)
        tyd = abs(ny - ty)

        val = ds2 * w_to - opp_push * w_avoid + (txd + tyd)
        # Prefer moves that improve distance primarily.
        improve = (ds2 < ds0)
        tie = (0 if improve else 1, val, txd, tyd, dx, dy)
        if bestm is None or tie < bestm[0]:
            bestm = (tie, [dx, dy])

    return bestm[1]