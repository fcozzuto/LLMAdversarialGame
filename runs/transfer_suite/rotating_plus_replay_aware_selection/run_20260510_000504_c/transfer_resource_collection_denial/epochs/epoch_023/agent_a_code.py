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

    def inb(x, y): return 0 <= x < w and 0 <= y < h
    def md(ax, ay, bx, by): return abs(ax - bx) + abs(ay - by)

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    if not resources:
        # drift toward center-ish while staying safe
        tx, ty = w // 2, h // 2
        best = [0, 0, None]
        for dx, dy in deltas:
            nx, ny = sx + dx, sy + dy
            if not inb(nx, ny) or (nx, ny) in obstacles:
                continue
            d = md(nx, ny, tx, ty)
            if best[0] is None or d < best[0]:
                best = [d, 0, (dx, dy)]
        return [best[2][0], best[2][1]] if best[2] is not None else [0, 0]

    # Precompute distances from opponent for each resource
    opp_d = [(p, md(p[0], p[1], ox, oy)) for p in resources]

    best_step = (0, 0)
    best_val = None
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue

        # Choose target by margin; also add local "swing" score to reduce opponent leads.
        best_margin = -10**9
        best_self_d = 10**9
        swing = 0
        for (px, py), od in opp_d:
            sd = md(nx, ny, px, py)
            margin = od - sd
            if sd == 0:
                margin += 5  # strong bias to pick up immediately
            if sd <= 3:
                swing += margin
            if (margin > best_margin) or (margin == best_margin and sd < best_self_d):
                best_margin = margin
                best_self_d = sd

        # Prevent getting too close to opponent while still moving for margin
        opp_next = md(nx, ny, ox, oy)
        val = (best_margin * 1000) + (swing * 10) - (opp_next)

        # Tie-break deterministically: prefer smaller self distance to best target, then lexicographic move
        if best_val is None or val > best_val:
            best_val = val
            best_step = (dx, dy)
        elif val == best_val:
            if best_self_d < md(sx + best_step[0], sy + best_step[1], resources[0][0], resources[0][1]):
                best_step = (dx, dy)
            else:
                if (dx, dy) < best_step:
                    best_step = (dx, dy)

    return [int(best_step[0]), int(best_step[1])]