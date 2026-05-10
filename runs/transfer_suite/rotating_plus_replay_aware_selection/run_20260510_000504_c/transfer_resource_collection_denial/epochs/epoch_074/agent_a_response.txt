def choose_move(observation):
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)

    obstacles = set()
    for p in observation.get("obstacles", []) or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obstacles.add((int(p[0]), int(p[1])))
        elif isinstance(p, dict):
            q = p.get("position", None)
            if isinstance(q, (list, tuple)) and len(q) >= 2:
                obstacles.add((int(q[0]), int(q[1])))
            else:
                if "x" in p and "y" in p:
                    obstacles.add((int(p["x"]), int(p["y"])))

    resources = []
    for r in observation.get("resources", []) or []:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            resources.append((int(r[0]), int(r[1])))
        elif isinstance(r, dict):
            q = r.get("position", None)
            if isinstance(q, (list, tuple)) and len(q) >= 2:
                resources.append((int(q[0]), int(q[1])))
            elif "x" in r and "y" in r:
                resources.append((int(r["x"]), int(r["y"])))

    def in_bounds(x, y):
        return 0 <= x < w and 0 <= y < h

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    moves = [(0, 0), (-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 1), (1, -1), (1, 0), (1, 1)]
    best = None
    for dxm, dym in moves:
        nx, ny = sx + dxm, sy + dym
        if not in_bounds(nx, ny):
            continue
        if (nx, ny) in obstacles:
            continue
        if resources:
            best_score = None
            for rx, ry in resources:
                myd = cheb(nx, ny, rx, ry)
                opd = cheb(ox, oy, rx, ry)
                # Prefer resources where we are closer than the opponent (tempo advantage)
                score = (opd - myd) * 100 - myd
                # Small deterministic tie-break: favor higher x then y
                score = score * 1000 + (rx * 8 + ry)
                if best_score is None or score > best_score:
                    best_score = score
            score = best_score
        else:
            # No visible resources: drift toward opponent-side resources area (opponent current corner bias)
            score = -cheb(nx, ny, ox, oy)
        if best is None or score > best[0]:
            best = (score, dxm, dym)

    if best is None:
        return [0, 0]
    return [int(best[1]), int(best[2])]