def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
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

    rpos = []
    for r in resources:
        q = rep_cell(r)
        if q and inb(q[0], q[1]) and q not in blocked:
            rpos.append(q)
    if not rpos:
        return [0, 0]

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def cheb(a, b, c, d):
        dx = a - c
        dy = b - d
        return abs(dx) if abs(dx) > abs(dy) else abs(dy)

    best_target = None
    best_score = -10**9
    for (rx, ry) in sorted(rpos):
        ds = cheb(sx, sy, rx, ry)
        do = cheb(ox, oy, rx, ry)
        # Prefer targets we can reach much sooner than opponent; slight center bias.
        center_bias = -0.01 * cheb(w // 2, h // 2, rx, ry)
        score = (do - ds) * 10 + center_bias
        if score > best_score:
            best_score = score
            best_target = (rx, ry)

    tx, ty = best_target
    candidates = []
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in blocked:
            continue
        # Evaluate next step: maximize chance to secure target and avoid moving into opponent's immediate reach.
        dist_self = cheb(nx, ny, tx, ty)
        dist_opp = cheb(ox, oy, tx, ty)
        # Also penalize moving closer to opponent itself (to avoid giving an easy contest).
        opp_dist_after = cheb(nx, ny, ox, oy)
        val = (dist_opp - dist_self) * 10 + opp_dist_after * 0.1 - cheb(nx, ny, sx, sy) * 0.01
        candidates.append((val, dx, dy, nx, ny))
    if not candidates:
        return [0, 0]

    candidates.sort(key=lambda t: (-t[0], t[1], t[2]))
    return [int(candidates[0][1]), int(candidates[0][2])]