def choose_move(observation):
    def to_xy(v):
        if isinstance(v, (list, tuple)) and len(v) >= 2:
            return int(v[0]), int(v[1])
        return 0, 0

    sx, sy = to_xy(observation.get("self_position", [0, 0]))
    ox, oy = to_xy(observation.get("opponent_position", [0, 0]))
    gw = int(observation.get("grid_width", 8) or 8)
    gh = int(observation.get("grid_height", 8) or 8)

    obstacles = set()
    for it in observation.get("obstacles") or []:
        x, y = to_xy(it)
        if 0 <= x < gw and 0 <= y < gh:
            obstacles.add((x, y))

    resources = []
    for it in observation.get("resources") or []:
        x, y = to_xy(it)
        if 0 <= x < gw and 0 <= y < gh and (x, y) not in obstacles:
            resources.append((x, y))
    if not resources:
        return [0, 0]

    def dman(x1, y1, x2, y2):
        ax = x1 - x2
        if ax < 0:
            ax = -ax
        ay = y1 - y2
        if ay < 0:
            ay = -ay
        return ax + ay

    # Score resources by race advantage; tie-break by getting there sooner, then deterministically by coordinates.
    best = None
    best_key = None
    for rx, ry in resources:
        sd = dman(sx, sy, rx, ry)
        od = dman(ox, oy, rx, ry)
        gap = od - sd  # positive means we are closer
        # Small bias to counter row-sweeping: prefer resources that differ more in y from opponent (disrupts their sweeps).
        y_bias = abs(ry - oy) - abs(ry - sy)
        key = (gap, y_bias, -sd, -rx, -ry)
        if best_key is None or key > best_key:
            best_key = key
            best = (rx, ry)

    tx, ty = best

    # Choose a legal step that most reduces distance to target; prefer diagonal/forward moves deterministically.
    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best_m = [0, 0]
    best_md = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < gw and 0 <= ny < gh):
            continue
        if (nx, ny) in obstacles:
            continue
        md = dman(nx, ny, tx, ty)
        # Deterministic tie-break: lowest md, then deterministic move order.
        if best_md is None or md < best_md or (md == best_md and [dx, dy] < best_m):
            best_md = md
            best_m = [dx, dy]

    if best_md is None:
        return [0, 0]
    return best_m