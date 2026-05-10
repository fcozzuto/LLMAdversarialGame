def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation.get("self_position", [0, 0])[:2]
    ox, oy = observation.get("opponent_position", [0, 0])[:2]

    obstacles = set()
    for p in observation.get("obstacles", []) or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obstacles.add((int(p[0]), int(p[1])))

    resources = []
    for r in observation.get("resources", []) or []:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            resources.append((int(r[0]), int(r[1])))
        elif isinstance(r, dict):
            if "position" in r and isinstance(r["position"], (list, tuple)) and len(r["position"]) >= 2:
                resources.append((int(r["position"][0]), int(r["position"][1])))
            elif "x" in r and "y" in r:
                resources.append((int(r["x"]), int(r["y"])))

    resources = [p for p in resources if p not in obstacles]
    if not resources:
        return [0, 0]

    def md(ax, ay, bx, by):
        return abs(ax - bx) + abs(ay - by)

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    # Target policy: prefer resources where we are closer (tie-break by deterministic key).
    best = None
    best_key = None
    for tx, ty in resources:
        d_me = md(sx, sy, tx, ty)
        d_op = md(ox, oy, tx, ty)
        key = (d_me > d_op, d_me, d_op, tx, ty)  # we want d_me <= d_op; otherwise push further
        if best_key is None or key < best_key:
            best_key = key
            best = (tx, ty)

    tx, ty = best
    # If blocked-adjacent, choose move that reduces distance to target most while staying in-bounds.
    best_move = (0, 0)
    best_move_key = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if nx < 0 or nx >= w or ny < 0 or ny >= h:
            continue
        if (nx, ny) in obstacles:
            continue
        d = md(nx, ny, tx, ty)
        # Secondary: avoid stepping into squares the opponent is significantly closer to for the same target.
        opp_d = md(ox, oy, tx, ty)
        key = (d, abs((ox - nx)) + abs((oy - ny)), nx, ny, opp_d)
        if best_move_key is None or key < best_move_key:
            best_move_key = key
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]