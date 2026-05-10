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
            px, py = int(r[0]), int(r[1])
        elif isinstance(r, dict):
            if "position" in r and isinstance(r["position"], (list, tuple)) and len(r["position"]) >= 2:
                px, py = int(r["position"][0]), int(r["position"][1])
            elif "x" in r and "y" in r:
                px, py = int(r["x"]), int(r["y"])
            else:
                continue
        else:
            continue
        if 0 <= px < w and 0 <= py < h and (px, py) not in obstacles:
            resources.append((px, py))

    if not resources:
        return [0, 0]

    def md(ax, ay, bx, by):
        return abs(ax - bx) + abs(ay - by)

    best = None
    # Prefer resources we are closer to than opponent; otherwise block by choosing where opponent is farthest relative to us.
    for tx, ty in resources:
        sd = md(sx, sy, tx, ty)
        od = md(ox, oy, tx, ty)
        adv = sd - od  # smaller => more likely to win
        # Tie-break deterministically by coordinates and distance.
        key = (adv, sd, -od, tx, ty)
        if best is None or key < best[0]:
            best = (key, tx, ty)

    _, tx, ty = best
    dx = 0 if tx == sx else (1 if tx > sx else -1)
    dy = 0 if ty == sy else (1 if ty > sy else -1)

    nx, ny = sx + dx, sy + dy
    if (nx, ny) in obstacles or not (0 <= nx < w and 0 <= ny < h):
        # Fallback: try axis moves in deterministic order that avoid obstacles.
        cand = [(-dx, 0), (0, -dy), (dx, 0), (0, dy), (0, 0)]
        for cdx, cdy in cand:
            nx, ny = sx + cdx, sy + cdy
            if (nx, ny) not in obstacles and 0 <= nx < w and 0 <= ny < h:
                return [cdx, cdy]
        return [0, 0]
    return [dx, dy]