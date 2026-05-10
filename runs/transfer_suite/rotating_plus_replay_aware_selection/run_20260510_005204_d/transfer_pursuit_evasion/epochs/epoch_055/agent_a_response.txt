def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0]) or [0, 0]
    ox, oy = observation.get("opponent_position", [0, 0]) or [0, 0]
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    role = str(observation.get("self_role", "")).lower()
    evading = ("evader" in role) or ("runner" in role)

    blocked = set()
    for p in observation.get("obstacles", []) or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            blocked.add((int(p[0]), int(p[1])))

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    corners = [(0, 0), (w - 1, 0), (0, h - 1), (w - 1, h - 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def cheb(ax, ay, bx, by):
        ax, ay, bx, by = int(ax), int(ay), int(bx), int(by)
        a, b = ax - bx, ay - by
        return abs(a) if abs(a) > abs(b) else abs(b)

    def obs_prox(x, y):
        # penalty for being adjacent to obstacles (discourages getting "stuck" near blocks)
        p = 0
        for (bx, by) in blocked:
            if cheb(x, y, bx, by) == 1:
                p += 1
        return p

    # Deterministic tie-break: iterate moves in fixed order; use strict comparisons.
    best_move = moves[0]
    best_val = None

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in blocked:
            continue

        d_opp = cheb(nx, ny, ox, oy)
        d_corner = min(cheb(nx, ny, cx, cy) for cx, cy in corners)

        # If paths are obstructed, favor staying on the side that best preserves distance gradient.
        # Also bias to move along the sign of opponent relative position (prevents oscillations).
        step_sign_x = 0 if ox == nx else (1 if ox > nx else -1)
        step_sign_y = 0 if oy == ny else (1 if oy > ny else -1)
        align = (1 if dx == step_sign_x else 0) + (1 if dy == step_sign_y else 0)

        # Score shaping: pursuer minimize distance, evader maximize distance; both avoid obstacle adjacency.
        # Evader also prefers higher "corner distance" to avoid corner traps when possible.
        if evading:
            val = (1000 * d_opp) - (30 * d_corner) + (10 * obs_prox(nx, ny)) - (5 * align)
        else:
            val = (1000 * d_opp) + (50 * obs_prox(nx, ny)) - (10 * d_corner) - (5 * align)

        if best_val is None or (val < best_val if not evading else val > best_val):
            best_val = val
            best_move = [dx, dy]

    return best_move