def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position", [0, 0]) or [0, 0]
    op = observation.get("opponent_position", [w - 1, h - 1]) or [w - 1, h - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles", []) or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for r in observation.get("resources", []) or []:
        if r and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    if not resources:
        return [0, 0]

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0:
            dx = -dx
        dy = ay - by
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    # Choose target: maximize opponent pressure minus my distance, with a small tie-break to avoid far hops.
    best_tx, best_ty = resources[0]
    best_score = -10**18
    for tx, ty in resources:
        dm = cheb(sx, sy, tx, ty)
        do = cheb(ox, oy, tx, ty)
        # If I'm already closer, prioritize still; if opponent closer, fight by reducing gap.
        score = (do - dm) * 100 - dm
        # Slightly prefer targets closer to center to reduce path brittleness.
        score -= cheb(tx, ty, (w - 1) // 2, (h - 1) // 2)
        if score > best_score:
            best_score = score
            best_tx, best_ty = tx, ty

    # Deterministic opponent response: if opponent is much closer, move to reduce my distance to target AND
    # try to increase opponent distance from that same target (a "soft block" heuristic).
    my_tie = 0
    target_gap = cheb(ox, oy, best_tx, best_ty) - cheb(sx, sy, best_tx, best_ty)
    if target_gap >= 2:
        my_tie = 1

    best_move = (0, 0)
    best_val = -10**18
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        my_d = cheb(nx, ny, best_tx, best_ty)
        opp_d = cheb(ox, oy, best_tx, best_ty)

        # Primary: reduce distance to target.
        val = -my_d * 10
        # Secondary: if opponent is closer, try to keep opponent farther from target by moving in a way that
        # usually disrupts approach (approx: increase distance between me and opponent).
        if my_tie:
            val += (cheb(nx, ny, ox, oy) - cheb(sx, sy, ox, oy)) * 3
        # Tertiary: avoid moving into worse relative position (gap).
        val += (opp_d - my_d) * 2
        # Quaternary: gentle preference to not step away from board corners (keeps consistent routes).
        val -= cheb(nx, ny, 0, 0) * 0.01

        if val > best_val:
            best_val = val
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]