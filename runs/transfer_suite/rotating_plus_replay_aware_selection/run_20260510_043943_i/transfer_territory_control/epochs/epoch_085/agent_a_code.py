def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position") or (0, 0)
    sx, sy = int(sp[0]), int(sp[1])
    opp = observation.get("opponent_position") or (w - 1, h - 1)
    ox, oy = int(opp[0]), int(opp[1])

    obstacles = set()
    for p in (observation.get("obstacles") or []):
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    unclaimed = set()
    for p in (observation.get("unclaimed_cells") or []):
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                unclaimed.add((x, y))

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    def ok(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    best = None
    best_score = None
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not ok(nx, ny):
            continue
        man_opp = abs(nx - ox) + abs(ny - oy)
        on_un = 1 if (nx, ny) in unclaimed else 0
        # Prefer unclaimed cells; among them, closest to opponent (more pressure) and then far from opponent (safety).
        # Deterministic fixed scoring with weighted terms:
        score = (on_un * 100000) + (-man_opp * 10) + (-((nx - (w // 2)) ** 2 + (ny - (h // 2)) ** 2))
        key = (score, -dx, -dy)  # deterministic tie-break
        if best is None or key > best_score:
            best_score = key
            best = [dx, dy]

    return best if best is not None else [0, 0]