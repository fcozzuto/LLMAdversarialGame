def choose_move(observation):
    def pt(v):
        if isinstance(v, (list, tuple)) and len(v) >= 2:
            return int(v[0]), int(v[1])
        if isinstance(v, dict):
            if "position" in v:
                return pt(v["position"])
            if "x" in v and "y" in v:
                return int(v["x"]), int(v["y"])
        return 0, 0

    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sx, sy = pt(observation.get("self_position") or [0, 0])
    ox, oy = pt(observation.get("opponent_position") or [0, 0])

    obstacles = set()
    for p in observation.get("obstacles", []) or []:
        if isinstance(p, dict) and "position" in p:
            p = p["position"]
        x, y = pt(p)
        if 0 <= x < w and 0 <= y < h:
            obstacles.add((x, y))

    resources = []
    for r in observation.get("resources", []) or []:
        if isinstance(r, dict) and "position" in r:
            r = r["position"]
        x, y = pt(r)
        if 0 <= x < w and 0 <= y < h:
            resources.append((x, y))

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def inb(x, y): return 0 <= x < w and 0 <= y < h

    def best_target(x, y):
        if resources:
            # Choose nearest resource by squared distance; tie-break by coords
            tx, ty = resources[0]
            best = (tx - x) * (tx - x) + (ty - y) * (ty - y)
            for rx, ry in resources[1:]:
                d = (rx - x) * (rx - x) + (ry - y) * (ry - y)
                if d < best or (d == best and (rx, ry) < (tx, ty)):
                    tx, ty, best = rx, ry, d
            return tx, ty
        return ox, oy

    tx, ty = best_target(sx, sy)
    best_move = (0, 0)
    best_score = -10**18

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue
        # Prefer stepping onto a resource, otherwise reduce distance to target
        score = 0
        if (nx, ny) in resources:
            score += 10**6
        score += -(nx - tx) * (nx - tx) - (ny - ty) * (ny - ty)
        # Slightly penalize being closer to opponent (encourage safer play); deterministic
        score -= 0.01 * ((nx - ox) * (nx - ox) + (ny - oy) * (ny - oy))
        # Deterministic tie-break by move order
        if score > best_score or (score == best_score and (dx, dy) < best_move):
            best_score = score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]