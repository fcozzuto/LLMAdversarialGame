def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position", (0, 0)) or (0, 0)
    op = observation.get("opponent_position", (0, 0)) or (0, 0)
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles", []) or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obstacles.add((int(p[0]), int(p[1])))

    resources = []
    for r in observation.get("resources", []) or []:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            rx, ry = int(r[0]), int(r[1])
            if 0 <= rx < w and 0 <= ry < h:
                resources.append((rx, ry))

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    if not resources:
        if valid(sx + 1, sy):
            return [1, 0]
        if valid(sx, sy + 1):
            return [0, 1]
        return [0, 0]

    def dist(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    # Target: where we are relatively closer than opponent (steal pressure)
    best = None
    best_key = None
    for r in resources:
        ds = dist((sx, sy), r)
        do = dist((ox, oy), r)
        key = (-(do - ds), ds, r[0], r[1])  # maximize (do-ds), then min ds
        if best_key is None or key < best_key:
            best_key = key
            best = r
    tx, ty = best

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    # If stepping onto/next to opponent is good tactically, it will be chosen by score.
    best_move = (0, 0)
    best_val = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        ds_new = abs(nx - tx) + abs(ny - ty)
        do_new = abs(nx - ox) + abs(ny - oy)
        # Prefer getting closer to target and also keeping opponent farther from our new position.
        # Small wall/edge bias to avoid boundary hits by nudging toward interior.
        edge_pen = (nx == 0) + (nx == w - 1) + (ny == 0) + (ny == h - 1)
        # Also add minor preference to not move away from steal opportunity.
        steal_gain = (abs((ox - tx)) if False else 0)
        val = (ds_new, edge_pen, -do_new, -(abs((ox - nx)) + abs((oy - ny))))
        # Deterministic tie-break by move order already in moves list.
        if best_val is None or val < best_val:
            best_val = val
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]