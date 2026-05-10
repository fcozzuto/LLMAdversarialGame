def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    blocked = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                blocked.add((x, y))

    role = str(observation.get("self_role") or "").lower()
    is_evader = ("evader" in role) or ("escape" in role) or ("runner" in role) or ("flee" in role) or ("defender" in role)

    def legal(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in blocked

    deltas = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def dist_metrics(x, y):
        md = abs(x - ox) + abs(y - oy)
        cd = abs(x - ox) if abs(x - ox) > abs(y - oy) else abs(y - oy)
        return md, cd

    if is_evader:
        corners = [(0, 0), (0, h - 1), (w - 1, 0), (w - 1, h - 1)]
        tx, ty = max(corners, key=lambda c: abs(c[0] - ox) + abs(c[1] - oy))
    else:
        tx, ty = ox, oy

    best_move = (0, 0)
    best_score = None

    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not legal(nx, ny):
            continue
        md, cd = dist_metrics(nx, ny)
        # Greedy pursuit/evasion with obstacle-safe deterministic tie-breaking.
        if is_evader:
            # Prefer increasing distance; also drift toward farthest corner.
            tmd = abs(nx - tx) + abs(ny - ty)
            score = (md, cd, tmd, -(nx + ny), -abs(dx) - abs(dy))
        else:
            tmd = abs(nx - tx) + abs(ny - ty)
            # Primary: minimize capture distance; secondary: minimize to opponent position; tertiary: avoid moving "away".
            score = (-cd, -md, -tmd, (nx + ny), -(abs(dx) + abs(dy)))
        if best_score is None:
            best_score = score
            best_move = (dx, dy)
        else:
            if score > best_score:
                best_score = score
                best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]