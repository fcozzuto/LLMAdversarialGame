def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [w - 1, h - 1])
    resources = observation.get("resources") or []
    obstacles = observation.get("obstacles") or []
    obst = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obst.add((int(p[0]), int(p[1])))

    def ok(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obst

    def dist(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    # Target: go for resources where we are relatively closer than opponent (denial-aware)
    # Score key: (self_advantage, -self_d, -tx-t y parity-ish, bias by turn parity)
    best = None
    t = int(observation.get("turn_index", 0))
    for r in resources:
        if not (isinstance(r, (list, tuple)) and len(r) >= 2):
            continue
        tx, ty = int(r[0]), int(r[1])
        if not ok(tx, ty):
            continue
        sd = dist((sx, sy), (tx, ty))
        od = dist((ox, oy), (tx, ty))
        advantage = od - sd  # bigger => we are closer
        # Deterministic tie-break: prefer nearer and slight diagonal/turn bias
        key = (advantage, -sd, -((tx + ty + t) % 2), -(tx * 9 + ty))
        if best is None or key > best[0]:
            best = (key, (tx, ty))
    if best is None:
        return [0, 0]
    tx, ty = best[1]

    # One-step policy: choose move that reduces distance to target, with safety and denial-tie breaks
    deltas = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    best_move = (0, 0)
    best_key = None
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not ok(nx, ny):
            continue
        self_d = dist((nx, ny), (tx, ty))
        opp_d = dist((ox, oy), (tx, ty))
        # Prefer decreasing our distance; if equal, prefer making opponent relatively farther;
        # also avoid moves that increase overall distance from our position too much.
        key = (-self_d, -(opp_d - self_d), -abs(dx) - abs(dy), ((nx + ny + t) % 2))
        if best_key is None or key > best_key:
            best_key = key
            best_move = (dx, dy)

    # If all moves invalid, engine will keep in place; return stay.
    if best_key is None:
        return [0, 0]
    return [int(best_move[0]), int(best_move[1])]