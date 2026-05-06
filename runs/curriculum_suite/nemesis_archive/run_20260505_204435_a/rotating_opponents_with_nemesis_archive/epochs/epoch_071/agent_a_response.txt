def choose_move(observation):
    w = observation.get("grid_width", 8) or 8
    h = observation.get("grid_height", 8) or 8
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []

    blocked = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            blocked.add((p[0], p[1]))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def rep_cell(r):
        if isinstance(r, dict):
            q = r.get("position")
            if isinstance(q, (list, tuple)) and len(q) >= 2:
                return (q[0], q[1])
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            return (r[0], r[1])
        return None

    rpos = []
    for r in resources:
        q = rep_cell(r)
        if q and inb(q[0], q[1]) and q not in blocked:
            rpos.append(q)
    if not rpos:
        return [0, 0]

    cx, cy = w // 2, h // 2

    def cheb(a, b, c, d):
        dx = a - c
        dy = b - d
        return abs(dx) if abs(dx) > abs(dy) else abs(dy)

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best_move = (0, 0)
    best_val = -10**9

    # If opponent is "sweeping" (row/column pressure), prioritize moves that keep our approach diagonal-friendly:
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in blocked:
            continue

        our_center = cheb(nx, ny, cx, cy)
        # Evaluate best resource we can potentially secure (positive advantage) from next position
        best_adv = -10**9
        best_adv2 = -10**9
        for rx, ry in rpos:
            od = cheb(ox, oy, rx, ry)
            nd = cheb(nx, ny, rx, ry)
            adv = od - nd  # positive means we are closer/equal than opponent
            if adv > best_adv:
                best_adv2 = best_adv
                best_adv = adv
            elif adv > best_adv2:
                best_adv2 = adv

        # If no positive advantage, fall back to moving toward center and slightly away from opponent line
        opp_row = (oy == sy)
        opp_col = (ox == sx)
        line_bias = 0
        if opp_row:
            line_bias = -1 if ny == oy else 0
        if opp_col:
            line_bias = -1 if nx == ox else 0

        val = 5 * best_adv - 0.25 * our_center + line_bias
        # Encourage progress even when behind
        if best_adv <= 0:
            nearest = min(cheb(nx, ny, rx, ry) for rx, ry in rpos)
            val += 1.5 * (-nearest)

        if val > best_val:
            best_val = val
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]