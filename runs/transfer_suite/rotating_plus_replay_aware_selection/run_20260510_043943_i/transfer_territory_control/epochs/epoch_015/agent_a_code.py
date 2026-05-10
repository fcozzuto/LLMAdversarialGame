def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sx, sy = observation.get("self_position") or [0, 0]
    ox, oy = observation.get("opponent_position") or [None, None]
    sx, sy = int(sx), int(sy)
    try:
        ox, oy = int(ox), int(oy)
    except:
        ox, oy = None, None

    obstacles = set()
    for p in (observation.get("obstacles") or []):
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obstacles.add((int(p[0]), int(p[1])))

    moves = [(0, -1), (0, 1), (-1, 0), (1, 0), (0, 0)]
    best = None
    best_val = -10**18

    res = observation.get("resources") or []
    targets = []
    for p in res:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            targets.append((int(p[0]), int(p[1])))
    if not targets:
        targets = [(w // 2, h // 2)]
    else:
        # Prefer nearby targets deterministically
        targets.sort(key=lambda t: abs(t[0] - sx) + abs(t[1] - sy))

    def in_bounds(x, y):
        return 0 <= x < w and 0 <= y < h

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not in_bounds(nx, ny) or (nx, ny) in obstacles:
            continue
        # Score: approach nearest resource; also avoid opponent if known
        md = min(abs(nx - tx) + abs(ny - ty) for tx, ty in targets)
        val = -md * 1000
        if ox is not None and oy is not None:
            od = abs(nx - ox) + abs(ny - oy)
            val += od * 10
        if best is None or val > best_val:
            best_val = val
            best = [dx, dy]

    if best is None:
        return [0, 0]
    return best