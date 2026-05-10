def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position", [0, 0]) or [0, 0]
    op = observation.get("opponent_position", [0, 0]) or [0, 0]
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

    def cheb(a, b):
        return max(abs(a[0] - b[0]), abs(a[1] - b[1]))

    def in_bounds(x, y):
        return 0 <= x < w and 0 <= y < h

    moves = []
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            if in_bounds(nx, ny) and (nx, ny) not in obstacles:
                moves.append((dx, dy))

    def target_priority(res):
        # prefer resources we're closer to than opponent; otherwise still allow if no good option
        dme = cheb((sx, sy), res)
        dop = cheb((ox, oy), res)
        return (dop <= dme, dme, dop, res[0], res[1])

    resources_sorted = sorted(resources, key=target_priority)
    best_target = resources_sorted[0]
    best_target_fallback = resources_sorted[-1] if resources_sorted else best_target

    best_score = None
    best_move = (0, 0)
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        # Choose between likely winnable target and fallback deterministically
        dme_best = cheb((nx, ny), best_target)
        dme_fb = cheb((nx, ny), best_target_fallback)
        use_best = 1 if cheb((ox, oy), best_target) > cheb((nx, ny), best_target) else 0
        tgt = best_target if use_best else best_target_fallback
        dme = cheb((nx, ny), tgt)
        dop = cheb((ox, oy), tgt)
        # Score: maximize progress to target; also try to worsen opponent's approach (denial)
        score = (1000 - dme) + 0.15 * (dme - dop) + (0.001 if tgt == best_target else 0)
        if best_score is None or score > best_score or (score == best_score and (dx, dy) < best_move):
            best_score = score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]