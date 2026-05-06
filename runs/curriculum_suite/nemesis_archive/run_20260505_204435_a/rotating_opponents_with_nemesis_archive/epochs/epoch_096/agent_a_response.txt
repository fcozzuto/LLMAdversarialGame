def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles_raw = observation.get("obstacles", []) or []
    blocked = set()
    for p in obstacles_raw:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            blocked.add((int(p[0]), int(p[1])))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    resources = observation.get("resources", []) or []
    rpos = []
    for r in resources:
        x = y = None
        if isinstance(r, dict):
            q = r.get("position", None)
            if isinstance(q, (list, tuple)) and len(q) >= 2:
                x, y = int(q[0]), int(q[1])
        elif isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
        if x is not None and inb(x, y) and (x, y) not in blocked:
            rpos.append((x, y))

    if not rpos:
        return [0, 0]

    def cheb(a, b):
        dx = abs(a[0] - b[0])
        dy = abs(a[1] - b[1])
        return dx if dx > dy else dy

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best_move = (0, 0)
    best_val = None

    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in blocked:
            nx, ny = sx, sy

        best_r = None
        best_r_val = None
        for rx, ry in rpos:
            self_d = cheb((nx, ny), (rx, ry))
            opp_d = cheb((ox, oy), (rx, ry))
            # Prefer resources we can reach meaningfully and deny ones opponent is closer to.
            v = (opp_d - self_d) * 100 - self_d
            # Break ties deterministically toward closer-to-us resource.
            if best_r_val is None or v > best_r_val or (v == best_r_val and self_d < cheb((nx, ny), best_r)):
                best_r_val = v
                best_r = (rx, ry)

        # If all v are negative, still choose move minimizing our distance to the best target.
        if best_val is None or best_r_val > best_val:
            best_val = best_r_val
            best_move = (dx, dy)
        elif best_r_val == best_val:
            # Deterministic tie-break: prefer moves that reduce our Chebyshev distance to chosen best_r.
            cur_self = cheb((nx, ny), best_r)
            bx, by = best_move
            ox2, oy2 = sx + bx, sy + by
            if not inb(ox2, oy2) or (ox2, oy2) in blocked:
                ox2, oy2 = sx, sy
            prev_self = cheb((ox2, oy2), best_r)
            if cur_self < prev_self:
                best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]