def choose_move(observation):
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    obstacles = observation.get("obstacles") or []
    resources = observation.get("resources") or []

    obs = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obs.add((int(p[0]), int(p[1])))

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obs

    def manh(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0:
            dx = -dx
        dy = y1 - y2
        if dy < 0:
            dy = -dy
        return dx + dy

    move_dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    best = None
    for r in resources:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            rx, ry = int(r[0]), int(r[1])
            if valid(rx, ry):
                best = (0, 0, 0, 0)
                break

    if resources:
        targets = []
        for r in resources:
            if isinstance(r, (list, tuple)) and len(r) >= 2:
                rx, ry = int(r[0]), int(r[1])
                if valid(rx, ry):
                    targets.append((rx, ry))
        if targets:
            cx = ox
            cy = oy
            for dx, dy in move_dirs:
                nx, ny = int(sx) + dx, int(sy) + dy
                if not valid(nx, ny):
                    continue
                d_to_res = min(manh(nx, ny, tx, ty) for tx, ty in targets)
                d_to_opp = manh(nx, ny, cx, cy)
                # Prefer closer to resources; break ties by farther from opponent; then deterministic tie-break
                score = (d_to_res, -d_to_opp, nx, ny)
                if best is None or score < best[0]:
                    best = (score, dx, dy)

    if best is not None:
        return [int(best[1]), int(best[2])]

    # Fallback: move toward center while avoiding opponent when possible
    tx, ty = w // 2, h // 2
    best2 = None
    for dx, dy in move_dirs:
        nx, ny = int(sx) + dx, int(sy) + dy
        if not valid(nx, ny):
            continue
        score = (manh(nx, ny, tx, ty), -manh(nx, ny, ox, oy), nx, ny)
        if best2 is None or score < best2[0]:
            best2 = (score, dx, dy)
    if best2 is None:
        return [0, 0]
    return [int(best2[1]), int(best2[2])]