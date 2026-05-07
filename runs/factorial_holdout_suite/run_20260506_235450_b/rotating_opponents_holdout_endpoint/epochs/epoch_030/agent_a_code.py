def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)

    sp = observation.get("self_position") or (0, 0)
    op = observation.get("opponent_position") or (w - 1, h - 1)
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for a in observation.get("obstacles") or []:
        if isinstance(a, dict) and "x" in a and "y" in a:
            x, y = int(a["x"]), int(a["y"])
        elif isinstance(a, (list, tuple)) and len(a) >= 2:
            x, y = int(a[0]), int(a[1])
        else:
            continue
        if 0 <= x < w and 0 <= y < h:
            obstacles.add((x, y))

    resources = []
    for r in observation.get("resources") or []:
        if isinstance(r, dict) and "x" in r and "y" in r:
            x, y = int(r["x"]), int(r["y"])
        elif isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
        else:
            continue
        if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
            resources.append((x, y))

    def cheb(x1, y1, x2, y2):
        a = x1 - x2
        if a < 0: a = -a
        b = y1 - y2
        if b < 0: b = -b
        return a if a > b else b

    dirs = [(0, 0), (1, 0), (-1, 0), (0, 1), (0, -1)]
    if not resources:
        # If no resources, move to increase distance from opponent deterministically.
        best = None
        for dx, dy in dirs:
            nx, ny = sx + dx, sy + dy
            if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles:
                score = cheb(nx, ny, ox, oy)
                if best is None or score > best[0]:
                    best = (score, dx, dy)
        return [best[1], best[2]] if best else [0, 0]

    # Pick nearest resource (by Chebyshev) deterministically.
    best_tx, best_ty = resources[0]
    best_dist = cheb(sx, sy, best_tx, best_ty)
    for tx, ty in resources[1:]:
        d = cheb(sx, sy, tx, ty)
        if d < best_dist or (d == best_dist and (tx < best_tx or (tx == best_tx and ty < best_ty))):
            best_dist = d
            best_tx, best_ty = tx, ty

    # Greedy one-step heuristic: get closer to target, avoid opponent, prefer landing on resource.
    best = None
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h) or (nx, ny) in obstacles:
            continue
        target_d = cheb(nx, ny, best_tx, best_ty)
        opp_d = cheb(nx, ny, ox, oy)
        on_resource = 1 if (nx, ny) == (best_tx, best_ty) else 0
        score = (-target_d) + (0.6 * opp_d) + (2.0 * on_resource)
        if best is None or score > best[0]:
            best = (score, dx, dy)

    return [best[1], best[2]] if best else [0, 0]