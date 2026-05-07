def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obst = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obst.add((x, y))

    resources = []
    for r in observation.get("resources") or []:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obst:
                resources.append((x, y))

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx >= dy else dy

    def best_target():
        if not resources:
            return (w // 2, h // 2)
        best_key = None
        best_res = resources[0]
        for rx, ry in resources:
            ds = cheb(sx, sy, rx, ry)
            do = cheb(ox, oy, rx, ry)
            # Prefer denying (do - ds), then faster (small ds)
            key = (do - ds, -ds, -(rx + ry), -rx)
            if best_key is None or key > best_key:
                best_key = key
                best_res = (rx, ry)
        return best_res

    tx, ty = best_target()

    # Candidate moves: toward target, plus a deterministic fallback order
    deltas = []
    dx = 0 if tx == sx else (1 if tx > sx else -1)
    dy = 0 if ty == sy else (1 if ty > sy else -1)
    deltas.append((dx, dy))

    # Add other options (deterministic): closer to target cheb, avoid obstacles
    base = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    # Remove duplicate of the first move while preserving order
    seen0 = set([deltas[0]])
    deltas += [d for d in base if d not in seen0]

    best = None
    for mx, my in deltas:
        nx, ny = sx + mx, sy + my
        if not (0 <= nx < w and 0 <= ny < h):
            continue
        if (nx, ny) in obst:
            continue
        # Heuristic: minimize distance to target, then minimize opponent distance (block), then bias toward resources
        d_to = cheb(nx, ny, tx, ty)
        d_opp = cheb(nx, ny, ox, oy)
        # Small preference for moving onto a resource if present
        on_res = 1 if (nx, ny) in set(resources) else 0
        key = (-on_res, d_to, d_opp, (nx + ny))
        if best is None or key < best[0]:
            best = (key, (mx, my))

    if best is None:
        # Deterministic safe fallback
        return [0, 0]
    return [int(best[1][0]), int(best[1][1])]