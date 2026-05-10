def choose_move(observation):
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)

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

    if not resources:
        return [0, 0]

    def md(ax, ay, bx, by):
        return abs(ax - bx) + abs(ay - by)

    best = None
    best_key = None
    for rx, ry in resources:
        if (rx, ry) in obstacles:
            continue
        ds = md(sx, sy, rx, ry)
        do = md(ox, oy, rx, ry)
        if best is None or (ds - 0.6 * do, ds, -rx, -ry) < best_key:
            best = (rx, ry)
            best_key = (ds - 0.6 * do, ds, -rx, -ry)

    if best is None:
        return [0, 0]
    tx, ty = best

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    # Prefer moves that get us onto the target or reduce distance to it; break ties by increasing distance from opponent
    cur_ds = md(sx, sy, tx, ty)
    best_move = (0, 0)
    best_move_key = None
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if nx < 0 or nx >= w or ny < 0 or ny >= h:
            continue
        if (nx, ny) in obstacles:
            continue
        nds = md(nx, ny, tx, ty)
        nod = md(nx, ny, ox, oy)
        # Higher nod is better (keep away from opponent), lower nds is better
        key = (0 if (nx == tx and ny == ty) else 1, nds, -nod, abs(dx) + abs(dy))
        if best_move_key is None or key < best_move_key or (key == best_move_key and nds < cur_ds):
            best_move_key = key
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]