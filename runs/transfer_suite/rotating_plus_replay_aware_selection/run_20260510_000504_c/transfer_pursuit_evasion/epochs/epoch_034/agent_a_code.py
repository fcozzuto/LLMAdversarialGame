def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))

    moves = [(0, 0), (1, 0), (-1, 0), (0, 1), (0, -1), (1, 1), (1, -1), (-1, 1), (-1, -1)]
    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def role_flags():
        s = (observation.get("self_role", "") or "").lower()
        o = (observation.get("opponent_role", "") or "").lower()
        if any(k in s for k in ("evad", "escape", "runner")):
            return True
        if any(k in o for k in ("evad", "escape", "runner")):
            return False
        if any(k in s for k in ("purs", "chase")):
            return False
        return False

    evader = role_flags()

    resources = observation.get("resources", None)
    if resources is None:
        resources = []
    if isinstance(resources, dict):
        res_list = list(resources.keys())
    else:
        res_list = list(resources)

    def dist2(a, b, c, d):
        x, y = a - c, b - d
        return x * x + y * y

    best_move = moves[0]
    best_val = -10**18
    rcount = observation.get("remaining_resource_count", None)
    has_res = bool(res_list) if rcount is None else (int(rcount) > 0)

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        d_opp = dist2(nx, ny, ox, oy)
        opp_term = d_opp if evader else -d_opp

        res_term = 0
        if has_res and res_list:
            best = None
            for r in res_list:
                rx, ry = (r[0], r[1]) if isinstance(r, (list, tuple)) and len(r) >= 2 else (r, r)
                v = dist2(nx, ny, rx, ry)
                if best is None or v < best:
                    best = v
            res_term = -best if best is not None else 0

        edge = min(nx, ny, w - 1 - nx, h - 1 - ny)
        wall_term = edge if evader else -edge

        val = opp_term * 3 + res_term * 2 + wall_term
        if val > best_val:
            best_val = val
            best_move = [dx, dy]

    return best_move if inb(sx + best_move[0], sy + best_move[1]) else [0, 0]