def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = set()
    for p in observation.get("obstacles", []) or []:
        try:
            px, py = int(p[0]), int(p[1])
            if 0 <= px < w and 0 <= py < h:
                obstacles.add((px, py))
        except:
            pass

    resources = []
    for r in observation.get("resources", []) or []:
        try:
            rx, ry = int(r[0]), int(r[1])
            if 0 <= rx < w and 0 <= ry < h and (rx, ry) not in obstacles:
                resources.append((rx, ry))
        except:
            pass

    deltas = [(-1,-1),(0,-1),(1,-1),(-1,0),(0,0),(1,0),(-1,1),(0,1),(1,1)]
    best = None
    best_score = None

    def dist(a, b):
        ax, ay = a; bx, by = b
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx + dy

    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h): 
            continue
        if (nx, ny) in obstacles:
            continue

        if resources:
            dres = min(dist((nx, ny), res) for res in resources)
        else:
            dres = None

        # Prefer reducing distance to nearest resource; if none, drift toward center; avoid opponent if tied.
        if dres is not None:
            # Small deterministic preference to stop if already on a resource
            score = (0 if any((nx == rx and ny == ry) for rx, ry in resources) else 1, dres)
        else:
            cx, cy = (w - 1) // 2, (h - 1) // 2
            score = (2, dist((nx, ny), (cx, cy)))

        # Tie-break: smaller distance to opponent (to compete) but deterministic
        score = (score[0], score[1], dist((nx, ny), (ox, oy)))
        if best_score is None or score < best_score:
            best_score = score
            best = (dx, dy)

    if best is None:
        return [0, 0]
    return [best[0], best[1]]