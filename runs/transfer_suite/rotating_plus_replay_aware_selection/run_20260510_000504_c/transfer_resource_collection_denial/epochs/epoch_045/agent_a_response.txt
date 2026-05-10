def choose_move(observation):
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

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

    width = int(observation.get("grid_width") or 8)
    height = int(observation.get("grid_height") or 8)

    def inside(x, y):
        return 0 <= x < width and 0 <= y < height

    def my_step_toward(tx, ty, x, y):
        dx = 0 if tx == x else (1 if tx > x else -1)
        dy = 0 if ty == y else (1 if ty > y else -1)
        return dx, dy

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    best = None
    best_move = (0, 0)

    for tx, ty in resources:
        my_d = max(abs(tx - sx), abs(ty - sy))
        op_d = max(abs(tx - ox), abs(ty - oy))
        gain = op_d - my_d  # prefer being closer than opponent
        tie = my_d  # closer first
        # also prefer resources in "front" direction to reduce dithering
        front = (tx - sx) + (ty - sy) * 0.01
        key = (-gain, tie, -front, tx, ty)

        dx_t, dy_t = my_step_toward(tx, ty, sx, sy)
        preferred = (dx_t, dy_t)
        # evaluate candidate next positions with obstacle avoidance
        for dx, dy in deltas:
            nx, ny = sx + dx, sy + dy
            if not inside(nx, ny) or (nx, ny) in obstacles:
                continue
            nd = max(abs(tx - nx), abs(ty - ny))
            # score: immediate progress and winning priority vs opponent
            my_improve = my_d - nd
            op_future = max(abs(tx - (ox + dx_t)), abs(ty - (oy + dy_t)))
            # if opponent is likely closer, discount
            score = (my_improve * 100) + (gain * 10) - nd + (0.001 if (dx, dy) == preferred else 0)
            cand = (key, -score)
            if best is None or cand < best:
                best = cand
                best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]