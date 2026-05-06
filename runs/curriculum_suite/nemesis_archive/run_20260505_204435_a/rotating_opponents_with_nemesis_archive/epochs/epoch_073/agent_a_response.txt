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
            blocked.add((int(p[0]), int(p[1])))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def rep_cell(r):
        if isinstance(r, dict):
            q = r.get("position")
            if isinstance(q, (list, tuple)) and len(q) >= 2:
                return (int(q[0]), int(q[1]))
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            return (int(r[0]), int(r[1]))
        return None

    def distc(x1, y1, x2, y2):
        dx = x1 - x2
        dy = y1 - y2
        return abs(dx) if abs(dx) > abs(dy) else abs(dy)

    rpos = []
    for r in resources:
        q = rep_cell(r)
        if q and inb(q[0], q[1]) and q not in blocked:
            rpos.append(q)
    if not rpos:
        return [0, 0]

    # Pick a target we are likely to reach sooner than the opponent.
    best_r = None
    best_key = None
    for rx, ry in rpos:
        ds = distc(sx, sy, rx, ry)
        do = distc(ox, oy, rx, ry)
        # Prefer resources where we are not behind; otherwise minimize how far behind we are.
        key = (0 if ds <= do else 1, ds - do, ds, rx, ry)
        if best_key is None or key < best_key:
            best_key = key
            best_r = (rx, ry)

    rx, ry = best_r
    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best_move = (0, 0)
    best_score = None

    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in blocked:
            continue
        ds_new = distc(nx, ny, rx, ry)
        do_new = distc(nx, ny, ox, oy)

        # Avoid drifting into opponent while advancing the target.
        # Deterministic tie-break uses (nx, ny).
        target_gain = (distc(sx, sy, rx, ry) - ds_new)
        opp_clear = do_new
        score = (-(ds_new), -abs(ds_new - (distc(sx, sy, rx, ry) - 1)), opp_clear + 0.1 * target_gain, -dx, -dy, nx, ny)
        if best_score is None or score > best_score:
            best_score = score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]