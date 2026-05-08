def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obstacles.add((int(p[0]), int(p[1])))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    resources = []
    for r in observation.get("resources") or []:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            resources.append((int(r[0]), int(r[1])))
        elif isinstance(r, dict) and "position" in r:
            pr = r["position"]
            if isinstance(pr, (list, tuple)) and len(pr) >= 2:
                resources.append((int(pr[0]), int(pr[1])))

    dirs = [(-1, 0), (0, -1), (0, 0), (0, 1), (1, 0), (-1, -1), (-1, 1), (1, -1), (1, 1)]
    targets = [t for t in resources if inb(t[0], t[1])]
    best_move = (0, 0)
    best_score = -10**18

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        if targets:
            md = 10**9
            for tx, ty in targets:
                d = abs(nx - tx) + abs(ny - ty)
                if d < md:
                    md = d
            # Prefer closer to nearest resource; tie-break by being closer to opponent (more pressure)
            score = -md * 1000 - (abs(nx - ox) + abs(ny - oy))
        else:
            # No known resources: move toward opponent
            score = -(abs(nx - ox) + abs(ny - oy))
        if score > best_score:
            best_score = score
            best_move = [dx, dy]

    return best_move