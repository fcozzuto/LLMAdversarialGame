def choose_move(observation):
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))

    obstacles = set()
    for p in observation.get("obstacles", []) or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obstacles.add((int(p[0]), int(p[1])))
        elif isinstance(p, dict):
            if "position" in p and isinstance(p["position"], (list, tuple)) and len(p["position"]) >= 2:
                obstacles.add((int(p["position"][0]), int(p["position"][1])))
            elif "x" in p and "y" in p:
                obstacles.add((int(p["x"]), int(p["y"])))

    resources = []
    for r in observation.get("resources", []) or []:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            resources.append((int(r[0]), int(r[1])))
        elif isinstance(r, dict):
            if "position" in r and isinstance(r["position"], (list, tuple)) and len(r["position"]) >= 2:
                resources.append((int(r["position"][0]), int(r["position"][1])))
            elif "x" in r and "y" in r:
                resources.append((int(r["x"]), int(r["y"])))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    if not resources:
        return [0, 0]

    def dist(x1, y1, x2, y2):
        dx = abs(x1 - x2)
        dy = abs(y1 - y2)
        return dx if dx >= dy else dy  # Chebyshev for 8-dir movement

    best_t = None
    best_key = None
    for tx, ty in resources:
        ds = dist(sx, sy, tx, ty)
        do = dist(ox, oy, tx, ty)
        key = (ds - 0.35 * do, ds, tx, ty)  # prefer closer, and farther from opponent
        if best_key is None or key < best_key:
            best_key = key
            best_t = (tx, ty)

    tx, ty = best_t
    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best_move = (0, 0)
    best_metric = None

    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue
        ds2 = dist(nx, ny, tx, ty)
        do2 = dist(ox, oy, tx, ty)
        metric = (ds2 - 0.10 * do2, ds2, abs(tx - nx) + abs(ty - ny), dx, dy)
        if best_metric is None or metric < best_metric:
            best_metric = metric
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]