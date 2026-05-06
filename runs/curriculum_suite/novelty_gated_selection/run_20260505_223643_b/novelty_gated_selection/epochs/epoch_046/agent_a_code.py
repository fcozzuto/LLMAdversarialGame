def choose_move(observation):
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)

    obstacles_raw = observation.get("obstacles", []) or []
    obstacles = set()
    for p in obstacles_raw:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
        elif isinstance(p, dict) and "position" in p:
            q = p["position"]
            if isinstance(q, (list, tuple)) and len(q) >= 2:
                x, y = int(q[0]), int(q[1])
            else:
                continue
        else:
            continue
        if 0 <= x < w and 0 <= y < h:
            obstacles.add((x, y))

    resources_raw = observation.get("resources", []) or []
    targets = []
    for r in resources_raw:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
        elif isinstance(r, dict):
            if "position" in r and isinstance(r["position"], (list, tuple)) and len(r["position"]) >= 2:
                x, y = int(r["position"][0]), int(r["position"][1])
            elif "x" in r and "y" in r:
                x, y = int(r["x"]), int(r["y"])
            else:
                continue
        else:
            continue
        if 0 <= x < w and 0 <= y < h:
            if (x, y) not in obstacles:
                targets.append((x, y))

    if not targets:
        return [0, 0]

    def manh(a, b, c, d):
        return abs(a - c) + abs(b - d)

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best = None
    best_score = -10**18

    for dx, dy in moves:
        nx, ny = int(sx + dx), int(sy + dy)
        if nx < 0 or nx >= w or ny < 0 or ny >= h:
            continue
        if (nx, ny) in obstacles:
            score = -10**12
        else:
            dist_to_res = min(manh(nx, ny, tx, ty) for tx, ty in targets)
            dist_to_opp = manh(nx, ny, ox, oy)
            score = -2 * dist_to_res + 0.4 * dist_to_opp
        if score > best_score or (score == best_score and (dx, dy) < best):
            best_score = score
            best = (dx, dy)

    return [best[0], best[1]]