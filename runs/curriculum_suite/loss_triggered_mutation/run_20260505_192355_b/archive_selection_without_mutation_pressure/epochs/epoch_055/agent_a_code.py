def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sp = observation.get("self_position", [0, 0])
    op = observation.get("opponent_position", [0, 0])
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    resources = observation.get("resources") or []
    if not resources:
        return [0, 0]

    obstacles = set((int(p[0]), int(p[1])) for p in (observation.get("obstacles") or []))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def steps(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0:
            dx = -dx
        dy = ay - by
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    def best_target():
        best = None
        for r in resources:
            rx, ry = int(r[0]), int(r[1])
            sd = steps(sx, sy, rx, ry)
            od = steps(ox, oy, rx, ry)
            # Prefer targets where we are closer; bias to smaller distances.
            adv = od - sd
            # If we are not closer, still consider but with a strong penalty.
            penalty = 0
            if adv < 0:
                penalty = (-adv) * 3
            # Tie-break: smaller self distance, and slightly farther from opponent to reduce contest.
            key = (adv - penalty, -sd, od - sd, rx, ry)
            if best is None or key > best[0]:
                best = (key, rx, ry)
        return best[1], best[2]

    tx, ty = best_target()

    moves = []
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            if inb(nx, ny):
                moves.append((dx, dy, nx, ny))
    if not moves:
        return [0, 0]

    bestm = None
    for dx, dy, nx, ny in moves:
        sd = steps(nx, ny, tx, ty)
        od = steps(ox, oy, tx, ty)
        # Move that improves our contest advantage; if equal, go closer to target; avoid approaching opponent.
        cur_adv = (od - sd)
        opp_dist = steps(nx, ny, ox, oy)
        key = (cur_adv, -sd, opp_dist, -abs(nx - tx) - abs(ny - ty), dx, dy)
        if bestm is None or key > bestm[0]:
            bestm = (key, dx, dy)
    return [int(bestm[1]), int(bestm[2])]